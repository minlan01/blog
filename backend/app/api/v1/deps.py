from datetime import datetime, timezone
from typing import Annotated
import hashlib
import time

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.models.access_token import AccessToken

DBSession = Annotated[Session, Depends(get_db)]

_ACTIVE_WHITELIST = {
    "/api/v1/auth/change-password",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
}

# PAT 爆破防护：IP 维度失败计数器
# 连续失败超过阈值 → 临时封锁该 IP 的 PAT 验证
_pat_failures: dict[str, list[float]] = {}  # ip → [失败时间戳列表]
_PAT_FAIL_THRESHOLD = 20  # 窗口内允许失败次数
_PAT_FAIL_WINDOW = 60  # 窗口大小（秒）
_PAT_LOCKOUT = 900  # 封锁时长（15 分钟）


def _get_client_ip(request: Request) -> str:
    return (
        request.headers.get("x-real-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host if request.client else "unknown"
    )


def _check_pat_rate_limit(ip: str) -> bool:
    """检查 IP 是否被临时封锁。返回 True = 允许，False = 封锁中。"""
    now = time.time()
    failures = _pat_failures.get(ip, [])
    # 清理过期记录
    failures = [t for t in failures if now - t < _PAT_LOCKOUT]
    _pat_failures[ip] = failures
    # 检查是否在封锁期
    if len(failures) >= _PAT_FAIL_THRESHOLD:
        latest = failures[-1]
        if now - latest < _PAT_LOCKOUT:
            return False
        else:
            _pat_failures.pop(ip, None)
    return True


def _record_pat_failure(ip: str) -> None:
    """记录一次 PAT 验证失败"""
    now = time.time()
    failures = _pat_failures.get(ip, [])
    failures = [t for t in failures if now - t < _PAT_FAIL_WINDOW]
    failures.append(now)
    _pat_failures[ip] = failures


def _clear_pat_failures(ip: str) -> None:
    """验证成功后清除失败记录"""
    _pat_failures.pop(ip, None)


def _extract_token(request: Request) -> str | None:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def _resolve_pat(token_value: str, db: Session) -> User | None:
    """解析 Personal Access Token，返回对应用户（或 None）"""
    token_hash = hashlib.sha256(token_value.encode()).hexdigest()
    pat = db.scalar(
        select(AccessToken).where(
            AccessToken.token_hash == token_hash,
            AccessToken.revoked == False,
        )
    )
    if not pat:
        return None
    # 检查过期
    if pat.expires_at and pat.expires_at < datetime.now(timezone.utc):
        return None
    # 更新最后使用时间
    pat.last_used_at = datetime.now(timezone.utc)
    db.commit()
    user = db.get(User, pat.user_id)
    if not user:
        return None
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        return None
    return user


def get_current_user(request: Request, db: DBSession) -> User:
    """Bottom layer: JWT access_token 或 Personal Access Token 均可。"""
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token provided")

    # PAT 识别：令牌以 pat_ 开头
    if token.startswith("pat_"):
        ip = _get_client_ip(request)
        # 爆破防护：检查 IP 是否被临时封锁
        if not _check_pat_rate_limit(ip):
            raise HTTPException(status_code=429, detail="Too many failed attempts, try again later")
        user = _resolve_pat(token, db)
        if not user:
            _record_pat_failure(ip)
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
        _clear_pat_failures(ip)
        return user

    # JWT access_token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # 校验 token 版本号：改密/重置后旧 token 立即失效
    token_ver = payload.get("ver", 0)
    if token_ver != user.token_version:
        raise HTTPException(status_code=401, detail="Token has been invalidated, please login again")
    return user


def _normalize_path(path: str) -> str:
    """Normalize URL path: strip trailing slash for consistent matching."""
    if len(path) > 1 and path.endswith("/"):
        return path.rstrip("/")
    return path


def require_active_user(request: Request, db: DBSession) -> User:
    """All routes that need an active user should use this.
    Blocks users with must_change_password=True except for whitelist paths."""
    user = get_current_user(request, db)
    path = _normalize_path(request.url.path)
    if user.must_change_password and path not in _ACTIVE_WHITELIST:
        raise HTTPException(status_code=423, detail="请先修改初始密码")
    return user


def require_super_admin(request: Request, db: DBSession) -> User:
    """Super admin check. Also goes through require_active_user."""
    user = require_active_user(request, db)
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user


CurrentUser = Annotated[User, Depends(require_active_user)]
SuperAdmin = Annotated[User, Depends(require_super_admin)]
