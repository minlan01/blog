"""结构化请求日志 — 内存环形缓冲，供 AI 运维接口查询"""
import time
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from fastapi import Request

# 环形缓冲：最近 2000 条请求记录
_BUFFER_SIZE = 2000
_buffer: deque = deque(maxlen=_BUFFER_SIZE)
_lock = Lock()

# 不记录日志的路径（避免 health check 刷屏）
_SKIP_PATHS = {"/health", "/api/v1/track"}


def log_request(
    method: str,
    path: str,
    status: int,
    elapsed_ms: float,
    ip: str,
    user_id: Optional[int],
    user_agent: str,
    error: Optional[str] = None,
) -> None:
    """记录一条请求日志到环形缓冲"""
    if path in _SKIP_PATHS:
        return
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "status": status,
        "elapsed_ms": round(elapsed_ms, 1),
        "ip": ip[:16] if ip else "unknown",  # 截断 IPv6 长地址
        "user_id": user_id,
        "user_agent": user_agent[:120] if user_agent else "",
        "error": error,
    }
    with _lock:
        _buffer.append(entry)


def get_logs(
    limit: int = 100,
    offset: int = 0,
    status_filter: Optional[int] = None,
    method_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
    error_only: bool = False,
) -> dict:
    """查询日志，支持过滤和分页"""
    with _lock:
        entries = list(_buffer)

    # 反转：最新的在前
    entries.reverse()

    # 过滤
    filtered = []
    for e in entries:
        if status_filter is not None and e["status"] != status_filter:
            continue
        if method_filter and e["method"] != method_filter.upper():
            continue
        if path_filter and path_filter.lower() not in e["path"].lower():
            continue
        if error_only and e["status"] < 400:
            continue
        filtered.append(e)

    total = len(filtered)
    page = filtered[offset : offset + limit]

    return {
        "total": total,
        "buffer_size": len(_buffer),
        "buffer_capacity": _BUFFER_SIZE,
        "logs": page,
    }


def clear_logs() -> int:
    """清空日志缓冲，返回清除的条数"""
    with _lock:
        count = len(_buffer)
        _buffer.clear()
    return count


def _extract_user_id(request: Request) -> Optional[int]:
    """从请求中提取用户 ID（不触发完整认证流程）"""
    # JWT token
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token.startswith("pat_"):
            # PAT 无法快速解析 user_id（需要查库），跳过
            return None
        try:
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                return int(payload["sub"])
        except Exception:
            pass
    return None


def _get_client_ip(request: Request) -> str:
    """提取真实客户端 IP"""
    return (
        request.headers.get("x-real-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host if request.client else "unknown"
    )
