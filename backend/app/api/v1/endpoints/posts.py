from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
import hashlib
import time
import logging

from app.api.v1.deps import DBSession
from app.core.cache import cache_get, cache_set
from app.core.config import settings
from app.models.post import Post
from app.models.site_config import SiteConfig
from app.schemas.post import PostDetail, PostSummary
from app.schemas.pagination import PaginatedResponse
from app.services.blog_service import BlogService

logger = logging.getLogger("blog")


# 浏览量去重：内存 LRU + TTL（IP+post_id 维度，24h 内只计一次）
_VIEW_DEDUP_TTL = 24 * 3600
_view_dedup: dict[str, float] = {}
_VIEW_DEDUP_MAX = 10000  # 最大条目数，避免内存暴涨


def _should_count_view(request: Request, post_id: int) -> bool:
    """判断是否应计入浏览量（24h 内同一 IP+文章只计一次）"""
    # 取真实 IP（nginx 转发）
    ip = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host if request.client else "unknown"
    key = hashlib.md5(f"{ip}:{post_id}".encode()).hexdigest()
    now = time.time()
    # 清理过期项（惰性清理）
    if len(_view_dedup) > _VIEW_DEDUP_MAX:
        expired = [k for k, t in _view_dedup.items() if now - t > _VIEW_DEDUP_TTL]
        for k in expired:
            _view_dedup.pop(k, None)
    if key in _view_dedup and now - _view_dedup[key] < _VIEW_DEDUP_TTL:
        return False
    _view_dedup[key] = now
    return True

logger = logging.getLogger("blog")

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
def list_posts(
    db: DBSession,
    featured: bool | None = Query(default=None),
    category: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
):
    if search:
        # FTS5 search path
        from app.services.fts_sync import execute_fts_search
        try:
            results, total = execute_fts_search(
                db.connection(), search,
                limit=per_page, offset=(page - 1) * per_page,
            )
        except OperationalError:
            return JSONResponse(
                status_code=503,
                content={"detail": "搜索服务暂时不可用，请稍后重试", "items": [], "total": 0},
            )

        # Fetch full Post objects for the matching rowids
        post_ids = [r["post_id"] for r in results]
        posts_map = {}
        if post_ids:
            posts = db.query(Post).filter(Post.id.in_(post_ids)).all()
            posts_map = {p.id: p for p in posts}

        # Build response, preserving FTS rank order
        items = []
        for r in results:
            p = posts_map.get(r["post_id"])
            if p:
                items.append({
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "summary": p.summary,
                    "cover_image": p.cover_image,
                    "published_at": p.published_at.isoformat() if p.published_at else None,
                    "reading_time": p.reading_time,
                    "category_id": p.category_id,
                    "content_snippet": r["content_snippet"],
                    "title_snippet": r["title_snippet"],
                })

        return {"items": items, "total": total, "page": page, "per_page": per_page}

    cache_key = f"posts:list:{featured}:{category}:{tag}:{page}:{per_page}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    service = BlogService(db)
    result = service.list_posts(
        featured=featured, category=category, tag=tag,
        search=None, page=page, per_page=per_page
    )

    cache_set(cache_key, result, 120)

    return result


@router.get("/{slug}", response_model=PostDetail)
def get_post(request: Request, slug: str, db: DBSession):
    service = BlogService(db)
    post = service.get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # 浏览量去重：24h 内同一 IP 只计一次
    if _should_count_view(request, post.id):
        db.execute(update(Post).where(Post.id == post.id).values(view_count=Post.view_count + 1))
        db.commit()
    db.refresh(post)
    return post


@router.get("/{slug}/related", response_model=list[PostSummary])
def get_related_posts(slug: str, db: DBSession, limit: int = Query(default=4, ge=1, le=10)):
    service = BlogService(db)
    post = service.get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return service.get_related_posts(post.id, limit)


@router.get("/{slug}/adjacent")
def get_adjacent_posts(slug: str, db: DBSession):
    """获取上一篇和下一篇已发布文章"""
    post = BlogService(db).get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    prev = db.scalar(
        select(Post)
        .where(Post.status == "published", Post.published_at < post.published_at, Post.id != post.id)
        .order_by(Post.published_at.desc())
        .limit(1)
    )
    next_post = db.scalar(
        select(Post)
        .where(Post.status == "published", Post.published_at > post.published_at, Post.id != post.id)
        .order_by(Post.published_at.asc())
        .limit(1)
    )
    return {
        "prev": {"slug": prev.slug, "title": prev.title} if prev else None,
        "next": {"slug": next_post.slug, "title": next_post.title} if next_post else None,
    }


@router.get("/{post_id}/og.png")
def get_og_image(post_id: int, db: DBSession):
    """Return a 1200x630 PNG for social media sharing (og:image).

    Cached on disk + 30-day Cache-Control header.
    """
    post = db.query(Post).options(joinedload(Post.category)).filter(Post.id == post_id).first()
    if not post or post.status != "published":
        raise HTTPException(status_code=404, detail="Post not found")

    # Get site name from DB
    site = db.query(SiteConfig).first()
    site_name = site.site_name if site else "Blog"

    from app.services.og_image import generate_og_image
    try:
        png_bytes = generate_og_image(post, site_name)
    except Exception as e:
        logger.error("OG image generation failed for post %s: %s", post_id, e)
        raise HTTPException(status_code=500, detail="Image generation failed")

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=2592000"},  # 30 days
    )
