from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select

from app.api.v1.deps import DBSession, _extract_token, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
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


@router.post("/register", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, body: UserCreate, db: DBSession):
    # Password complexity check
    errors = validate_password_strength(body.password)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    existing = db.scalar(select(User).where(User.username == body.username))
    if existing:
        raise HTTPException(status_code=409, detail="Username already registered")

    if body.email:
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


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: DBSession):
    user = db.scalar(select(User).where(User.username == body.username))

    # Check if account is locked
    if user and user.locked_until and user.locked_until > datetime.now(timezone.utc):
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
        raise HTTPException(
            status_code=423,
            detail=f"Account locked. Try again in {remaining} minutes.",
        )

    if not user or not verify_password(body.password, user.password_hash):
        # Increment failed attempts
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCK_DURATION_MINUTES)
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Reset failed attempts on success
    user.failed_login_attempts = 0
    user.locked_until = None

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    user.refresh_token = refresh_token
    db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(body: RefreshRequest, db: DBSession):
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    user = db.get(User, int(user_id))
    if not user or user.refresh_token != body.refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh = create_refresh_token(data={"sub": str(user.id)})
    user.refresh_token = new_refresh
    db.commit()

    return Token(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
def logout(request: Request, db: DBSession):
    user = get_current_user(request, db)
    user.refresh_token = None
    db.commit()


@router.get("/me", response_model=UserRead)
def get_profile(request: Request, db: DBSession):
    return get_current_user(request, db)


@router.put("/me", response_model=UserRead)
def update_profile(body: UserUpdate, request: Request, db: DBSession):
    user = get_current_user(request, db)
    if body.bio is not None:
        user.bio = body.bio
    if body.avatar is not None:
        user.avatar = body.avatar
    if body.email is not None:
        existing = db.scalar(select(User).where(User.email == body.email, User.id != user.id))
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = body.email
        user.email_verified = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest, db: DBSession):
    """Send password reset email. Always returns success to prevent email enumeration."""
    user = db.scalar(select(User).where(User.email == body.email))
    if user:
        from app.core.email import send_password_reset_email
        send_password_reset_email(user, db)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: DBSession):
    errors = validate_password_strength(body.new_password)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    payload = decode_refresh_token(body.token) if body.token else None
    # Use access token decode for reset tokens (they're JWT too)
    from app.core.security import decode_access_token
    payload = decode_access_token(body.token)
    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(body.new_password)
    user.refresh_token = None
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    return {"message": "Password reset successfully"}


@router.post("/verify-email")
def verify_email(body: VerifyEmailRequest, db: DBSession):
    from app.core.security import decode_access_token
    payload = decode_access_token(body.token)
    if not payload or payload.get("purpose") != "email_verify":
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.email_verified = True
    db.commit()
    return {"message": "Email verified successfully"}
