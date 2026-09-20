"""访问统计：采集端点 + 聚合查询"""
import hashlib
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select

from app.api.v1.deps import DBSession, SuperAdmin
from app.core.cache import cache_get, cache_set
from app.models.page_view import PageView

router = APIRouter(prefix="/track", tags=["tracking"])
limiter = Limiter(key_func=get_remote_address)

# 内存去重：ip_hash+path → 最后记录时间（10 秒内同 IP+同路径不重复记录）
_dedup: dict[str, float] = {}
_DEDUP_TTL = 10  # 秒
_DEDUP_MAX = 5000

# 搜索引擎识别
_SEARCH_ENGINES = {
    "google": "Google",
    "bing": "Bing",
    "baidu": "百度",
    "sogou": "搜狗",
    "duckduckgo": "DuckDuckGo",
    "yandex": "Yandex",
}


class TrackPayload(BaseModel):
    path: str = Field(..., min_length=1, max_length=500)
    referrer: str = Field(default="", max_length=500)


def _parse_device(ua: str) -> str:
    ua_lower = ua.lower()
    if "tablet" in ua_lower or "ipad" in ua_lower:
        return "tablet"
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        return "mobile"
    return "desktop"


def _parse_browser(ua: str) -> str:
    ua_lower = ua.lower()
    if "edg" in ua_lower:
        return "edge"
    if "chrome" in ua_lower and "chromium" not in ua_lower:
        return "chrome"
    if "safari" in ua_lower and "chrome" not in ua_lower:
        return "safari"
    if "firefox" in ua_lower:
        return "firefox"
    return "other"


def _parse_referrer(referrer: str) -> str:
    if not referrer:
        return "直接访问"
    ref_lower = referrer.lower()
    for engine_key, engine_name in _SEARCH_ENGINES.items():
        if engine_key in ref_lower:
            return engine_name
    # 提取域名
    try:
        from urllib.parse import urlparse
        host = urlparse(referrer).hostname or "外部链接"
        return host
    except Exception:
        return "外部链接"


@router.post("", status_code=204)
@limiter.limit("30/minute")
def track(request: Request, response: Response, body: TrackPayload, db: DBSession):
    """记录一次页面访问。防爆破：
    1. IP 维度 30 次/分钟 rate limit
    2. 同 IP + 同路径 10 秒内去重
    3. path 字段严格校验（必须以 / 开头）
    """
    # 校验路径格式
    if not body.path.startswith("/"):
        raise HTTPException(status_code=400)

    # 忽略静态资源和 API 调用
    if any(body.path.startswith(p) for p in ["/assets/", "/api/", "/sw.js", "/manifest.json"]):
        return Response(status_code=204)

    # 取真实 IP
    ip = (
        request.headers.get("x-real-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.client.host if request.client else "unknown"
    )
    ip_hash = hashlib.md5(ip.encode()).hexdigest()[:8]

    # 去重检查
    dedup_key = f"{ip_hash}:{body.path}"
    now = time.time()
    if dedup_key in _dedup and now - _dedup[dedup_key] < _DEDUP_TTL:
        return Response(status_code=204)

    # 惰性清理过期去重项
    if len(_dedup) > _DEDUP_MAX:
        expired = [k for k, t in _dedup.items() if now - t > _DEDUP_TTL]
        for k in expired:
            _dedup.pop(k, None)

    _dedup[dedup_key] = now

    # 解析 UA
    ua = request.headers.get("user-agent", "")

    # 解析来源
    ref_source = _parse_referrer(body.referrer)

    # 写入（同步，SQLite 单条 INSERT 极快）
    db.add(PageView(
        path=body.path,
        device=_parse_device(ua),
        browser=_parse_browser(ua),
        referrer_source=ref_source,
        ip_hash=ip_hash,
    ))
    db.commit()

    return Response(status_code=204)


@router.get("/stats")
def get_track_stats(admin: SuperAdmin, db: DBSession, days: int = 30):
    """聚合查询访问统计（后台用）。缓存 2 分钟。"""
    cache_key = f"track:stats:{days}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    since = datetime.now(timezone.utc) - timedelta(days=days)

    # 总访问量
    total = db.scalar(
        select(func.count()).select_from(PageView).where(PageView.created_at >= since)
    ) or 0

    # 设备分布
    device_rows = db.execute(
        select(PageView.device, func.count().label("c"))
        .where(PageView.created_at >= since)
        .group_by(PageView.device)
        .order_by(func.count().desc())
    ).all()

    # 浏览器分布
    browser_rows = db.execute(
        select(PageView.browser, func.count().label("c"))
        .where(PageView.created_at >= since)
        .group_by(PageView.browser)
        .order_by(func.count().desc())
    ).all()

    # 来源分布
    referrer_rows = db.execute(
        select(PageView.referrer_source, func.count().label("c"))
        .where(PageView.created_at >= since)
        .group_by(PageView.referrer_source)
        .order_by(func.count().desc())
        .limit(10)
    ).all()

    # 按天趋势
    trend_rows = db.execute(
        select(
            func.date(PageView.created_at).label("d"),
            func.count().label("c"),
        )
        .where(PageView.created_at >= since)
        .group_by(func.date(PageView.created_at))
        .order_by(func.date(PageView.created_at))
    ).all()

    # 页面排行
    page_rows = db.execute(
        select(PageView.path, func.count().label("c"))
        .where(PageView.created_at >= since)
        .group_by(PageView.path)
        .order_by(func.count().desc())
        .limit(10)
    ).all()

    # 唯一访客数
    unique_visitors = db.scalar(
        select(func.count(func.distinct(PageView.ip_hash)))
        .where(PageView.created_at >= since)
    ) or 0

    result = {
        "total_views": total,
        "unique_visitors": unique_visitors,
        "devices": [{"name": r.device, "count": r.c, "pct": round(r.c / total * 100) if total else 0} for r in device_rows],
        "browsers": [{"name": r.browser, "count": r.c, "pct": round(r.c / total * 100) if total else 0} for r in browser_rows],
        "referrers": [{"source": r.referrer_source, "count": r.c} for r in referrer_rows],
        "trend": [{"date": str(r.d), "count": r.c} for r in trend_rows],
        "top_pages": [{"path": r.path, "count": r.c} for r in page_rows],
    }

    cache_set(cache_key, result, 120)
    return result
