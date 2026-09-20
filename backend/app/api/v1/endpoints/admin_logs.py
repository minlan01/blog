"""AI 运维日志接口 — 供 AI/管理员查询后台请求日志

安全防护：
1. SuperAdmin 权限（PAT 或 JWT 认证）
2. Rate limit 20 次/分钟
3. 日志中 IP 截断存储，不记录完整地址
4. User-Agent 截断 120 字符
5. 敏感请求体/响应体不记录
"""
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.deps import SuperAdmin
from app.core.request_log import get_logs, clear_logs

router = APIRouter(prefix="/admin/logs", tags=["admin-logs"])
limiter = Limiter(key_func=get_remote_address)


@router.get("")
@limiter.limit("20/minute")
def query_logs(
    request: Request,
    admin: SuperAdmin,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: int | None = Query(None, description="按状态码过滤，如 401/500"),
    method: str | None = Query(None, description="按方法过滤：GET/POST/PUT/DELETE"),
    path: str | None = Query(None, description="按路径关键词过滤"),
    error_only: bool = Query(False, description="只看错误请求（4xx/5xx）"),
):
    """查询后台请求日志（最新在前）

    用法示例：
    - 最近 50 条：GET /admin/logs
    - 只看错误：GET /admin/logs?error_only=true
    - 查 401：GET /admin/logs?status=401
    - 查 POST 请求：GET /admin/logs?method=POST
    - 查包含 /posts 的请求：GET /admin/logs?path=posts
    """
    return get_logs(
        limit=limit,
        offset=offset,
        status_filter=status,
        method_filter=method,
        path_filter=path,
        error_only=error_only,
    )


@router.delete("")
@limiter.limit("5/minute")
def clear_all_logs(request: Request, admin: SuperAdmin):
    """清空日志缓冲"""
    count = clear_logs()
    return {"message": f"已清除 {count} 条日志", "cleared": count}


@router.get("/summary")
@limiter.limit("10/minute")
def logs_summary(request: Request, admin: SuperAdmin):
    """日志摘要统计"""
    data = get_logs(limit=500)
    logs = data["logs"]

    total = len(logs)
    errors = sum(1 for l in logs if l["status"] >= 400)
    avg_ms = sum(l["elapsed_ms"] for l in logs) / total if total else 0

    # 状态码分布
    status_dist: dict[str, int] = {}
    for l in logs:
        key = f"{l['status'] // 100}xx"
        status_dist[key] = status_dist.get(key, 0) + 1

    # 路径频率 Top 5
    path_freq: dict[str, int] = {}
    for l in logs:
        path_freq[l["path"]] = path_freq.get(l["path"], 0) + 1
    top_paths = sorted(path_freq.items(), key=lambda x: -x[1])[:5]

    # 最慢请求 Top 5
    slowest = sorted(logs, key=lambda x: -x["elapsed_ms"])[:5]

    return {
        "total_in_query": total,
        "buffer_size": data["buffer_size"],
        "buffer_capacity": data["buffer_capacity"],
        "error_count": errors,
        "error_rate": round(errors / total * 100, 1) if total else 0,
        "avg_response_ms": round(avg_ms, 1),
        "status_distribution": status_dist,
        "top_paths": [{"path": p, "count": c} for p, c in top_paths],
        "slowest_requests": slowest,
    }
