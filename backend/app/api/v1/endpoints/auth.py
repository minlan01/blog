from datetime import datetime, timedelta, timezone
import hashlib
import os
import random
import time

from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, File
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, update

from app.api.v1.deps import CurrentUser, DBSession, _extract_token
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_token_by_purpose,
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserRead,
    UserUpdate,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)

MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 30

# Cookie 配置
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 天


def _set_refresh_cookie(response: Response, token: str) -> None:
    """设置 httpOnly refresh_token cookie"""
    is_https = settings.SITE_URL.startswith("https://")
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=is_https,
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """清除 refresh_token cookie"""
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/v1/auth")


# ── 注册验证码 ──
def _generate_captcha_token(a: int, b: int, ts: int) -> str:
    raw = f"{a}+{b}:{ts}:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _verify_captcha(answer: int | None, token: str | None, ts: int | None) -> bool:
    if answer is None or token is None or ts is None:
        return False
    now = int(time.time())
    if now - ts > 600:
        return False
    for a in range(1, 21):
        for b in range(1, 21):
            if a + b == answer and _generate_captcha_token(a, b, ts) == token:
                return True
    return False


@router.get("/captcha")
def get_register_captcha():
    """算术验证码，用于注册防爆破"""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    ts = int(time.time())
    token = _generate_captcha_token(a, b, ts)
    return {"question": f"{a} + {b} = ?", "token": token, "ts": ts}


class RegisterWithCaptcha(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str
    captcha_answer: int
    captcha_token: str
    captcha_ts: int


@router.post("/register", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterWithCaptcha, db: DBSession):
    # 验证码校验
    if not _verify_captcha(body.captcha_answer, body.captcha_token, body.captcha_ts):
        raise HTTPException(status_code=400, detail="验证码错误")

    # 确认密码校验
    if body.password != body.confirm_password:
        raise HTTPException(status_code=422, detail="两次密码不一致")

    # Password complexity check
    errors = validate_password_strength(body.password)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    existing = db.scalar(select(User).where(User.username == body.username))
    if existing:
        raise HTTPException(status_code=409, detail="用户名已被注册")

    existing_email = db.scalar(select(User).where(User.email == body.email))
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/hcaptcha-config")
def get_hcaptcha_config():
    """hCaptcha 开关：两项密钥都配置时启用；未配置时登录流程与无验证码完全一致"""
    enabled = bool(settings.HCAPTCHA_SITEKEY and settings.HCAPTCHA_SECRET)
    return {"enabled": enabled, "sitekey": settings.HCAPTCHA_SITEKEY if enabled else ""}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, response: Response, body: LoginRequest, db: DBSession):
    if settings.HCAPTCHA_SECRET:
        if not body.hcaptcha_token:
            raise HTTPException(status_code=400, detail="请先完成 hCaptcha 人机验证")
        import httpx

        verify = httpx.post(
            "https://api.hcaptcha.com/siteverify",
            data={"secret": settings.HCAPTCHA_SECRET, "response": body.hcaptcha_token},
            timeout=10,
        )
        if not verify.json().get("success"):
            raise HTTPException(status_code=400, detail="hCaptcha 验证失败，请重试")

    user = db.scalar(select(User).where(User.username == body.username))

    # Check if account is locked
    if user and user.locked_until and user.locked_until > datetime.now(timezone.utc):
        remaining = max(1, int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60))
        raise HTTPException(
            status_code=423,
            detail=f"账号已锁定，请在 {remaining} 分钟后重试",
        )

    if not user or not verify_password(body.password, user.password_hash):
        if user:
            db.execute(
                update(User)
                .where(User.id == user.id)
                .values(failed_login_attempts=User.failed_login_attempts + 1)
            )
            db.execute(
                update(User)
                .where(User.id == user.id, User.failed_login_attempts >= MAX_FAILED_ATTEMPTS)
                .values(locked_until=datetime.now(timezone.utc) + timedelta(minutes=LOCK_DURATION_MINUTES))
            )
            db.commit()
            db.refresh(user)
            # 已被锁定
            if user.locked_until and user.locked_until > datetime.now(timezone.utc):
                remaining_min = max(1, int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60))
                raise HTTPException(
                    status_code=423,
                    detail=f"账号已锁定，请在 {remaining_min} 分钟后重试",
                )
            # 返回剩余尝试次数
            attempts_left = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
            raise HTTPException(
                status_code=401,
                detail=f"用户名或密码错误，剩余尝试次数 {attempts_left}",
            )
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Reset failed attempts on success
    user.failed_login_attempts = 0
    user.locked_until = None

    access_token = create_access_token(data={"sub": str(user.id)}, token_version=user.token_version)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    user.refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db.commit()

    # refresh_token 通过 httpOnly cookie 发放，前端不再持有
    _set_refresh_cookie(response, refresh_token)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, response: Response, db: DBSession):
    # 优先从 httpOnly cookie 读取，兼容旧版 body 中的 refresh_token
    refresh_token_value = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token_value:
        # 兼容性：允许从 body 传入（旧客户端）
        try:
            import json
            body = json.loads(request._body) if hasattr(request, '_body') else {}
        except Exception:
            body = {}
        refresh_token_value = body.get("refresh_token") if isinstance(body, dict) else None

    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="缺少刷新令牌")

    payload = decode_refresh_token(refresh_token_value)
    if not payload:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")

    user_id = payload.get("sub")
    user = db.get(User, int(user_id))

    token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
    if not user:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    if user.refresh_token_hash != token_hash:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    access_token = create_access_token(data={"sub": str(user.id)}, token_version=user.token_version)
    new_refresh = create_refresh_token(data={"sub": str(user.id)})
    user.refresh_token_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    db.commit()

    _set_refresh_cookie(response, new_refresh)

    return Token(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
def logout(response: Response, current_user: CurrentUser, db: DBSession):
    current_user.refresh_token_hash = None
    db.commit()
    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead)
def get_profile(current_user: CurrentUser):
    return current_user


@router.put("/me", response_model=UserRead)
@limiter.limit("5/minute")
def update_profile(body: UserUpdate, request: Request, current_user: CurrentUser, db: DBSession):
    if body.bio is not None:
        current_user.bio = body.bio
    if body.avatar is not None:
        current_user.avatar = body.avatar
    if body.email is not None:
        existing = db.scalar(select(User).where(User.email == body.email, User.id != current_user.id))
        if existing:
            raise HTTPException(status_code=409, detail="邮箱已被使用")
        current_user.email = body.email
        current_user.email_verified = False
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest, db: DBSession):
    """Send password reset email. Always returns success to prevent email enumeration."""
    from app.core.config import settings
    user = db.scalar(select(User).where(User.email == body.email))
    if user:
        if not settings.SMTP_HOST:
            raise HTTPException(
                status_code=503,
                detail="邮件服务未配置，请联系管理员重置密码",
            )
        from app.core.email import send_password_reset_email
        send_password_reset_email(user, db)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, body: ResetPasswordRequest, db: DBSession):
    errors = validate_password_strength(body.new_password)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    payload = decode_token_by_purpose(body.token, "password_reset")
    if not payload:
        raise HTTPException(status_code=400, detail="重置令牌无效或已过期")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 校验 token 版本：使重置后的旧 purpose token 立即失效（一次性）
    token_ver = payload.get("ver", -1)
    if token_ver != user.token_version:
        raise HTTPException(status_code=400, detail="重置令牌已使用，请重新申请")

    user.password_hash = hash_password(body.new_password)
    user.refresh_token_hash = None
    user.failed_login_attempts = 0
    user.locked_until = None
    # 原子递增 token_version，使所有已签发的 access_token 立即失效
    db.execute(update(User).where(User.id == user.id).values(token_version=User.token_version + 1))
    db.commit()
    return {"message": "密码重置成功"}


@router.post("/verify-email")
@limiter.limit("5/minute")
def verify_email(request: Request, body: VerifyEmailRequest, db: DBSession):
    payload = decode_token_by_purpose(body.token, "email_verify")
    if not payload:
        raise HTTPException(status_code=400, detail="验证令牌无效或已过期")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")

    user.email_verified = True
    db.commit()
    return {"message": "邮箱验证成功"}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
@limiter.limit("5/minute")
def change_password(request: Request, response: Response, body: ChangePasswordRequest, current_user: CurrentUser, db: DBSession):
    """Change password. Users with must_change_password=True can only access this + logout + me."""
    if not verify_password(body.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="旧密码不正确")

    errors = validate_password_strength(body.new_password)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    current_user.password_hash = hash_password(body.new_password)
    current_user.must_change_password = False
    current_user.refresh_token_hash = None  # Force re-login
    # 原子递增 token_version
    db.execute(update(User).where(User.id == current_user.id).values(token_version=User.token_version + 1))
    db.commit()
    _clear_refresh_cookie(response)

    return {"message": "密码修改成功，请重新登录"}


@router.post("/avatar")
@limiter.limit("10/minute")
async def upload_avatar(
    request: Request,
    current_user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...),
):
    """Upload avatar for current user. Returns the avatar URL."""

    # Validate file type
    allowed_types = {"image/png", "image/jpeg", "image/gif", "image/webp"}
    mime = (file.content_type or "").split(";")[0].strip().lower()
    if mime not in allowed_types:
        raise HTTPException(status_code=415, detail="只支持 PNG/JPEG/GIF/WebP 格式")

    # Size limit: 5MB for avatars
    max_bytes = 5 * 1024 * 1024
    data = await file.read()
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="头像文件不能超过 5MB")
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")

    # Compress and resize using Pillow
    try:
        import io as _io
        from PIL import Image as PILImage, ImageOps

        img = PILImage.open(_io.BytesIO(data))
        img = ImageOps.exif_transpose(img)

        # Resize to max 512x512
        max_dim = 512
        w, h = img.size
        if max(w, h) > max_dim:
            ratio = max_dim / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), PILImage.LANCZOS)

        # Convert to RGB for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            bg = PILImage.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = bg

        buf = _io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        data = buf.getvalue()
    except Exception:
        pass  # If Pillow fails, use original

    # Save to uploads directory — organized by user folder
    import uuid
    user_folder = f"{current_user.username}_{current_user.email or 'no-email'}"
    upload_dir = os.path.join("uploads", "images", user_folder)
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(data)

    # Save to Image model for tracking
    from app.models.image import Image
    img_record = Image(
        filename=filename,
        mime_type="image/jpeg",
        data=None,
        file_path=f"{user_folder}/{filename}",
        object_key=None,
        storage_backend="local",
        media_type="image",
        size=len(data),
        uploaded_by=user_folder,
    )
    db.add(img_record)
    db.commit()
    db.refresh(img_record)

    # Update user avatar — return absolute URL so it works everywhere
    avatar_url = f"{settings.SITE_URL}/api/v1/upload/{img_record.id}"
    current_user.avatar = avatar_url
    db.commit()

    return {"avatar": avatar_url}
