from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import update

from app.api.v1.deps import DBSession
from app.core.cache import cache_get, cache_set
from app.models.post import Post
from app.schemas.post import PostDetail, PostSummary
from app.schemas.pagination import PaginatedResponse
from app.services.blog_service import BlogService

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
    if not search:
        cache_key = f"posts:list:{featured}:{category}:{tag}:{page}:{per_page}"
        cached = cache_get(cache_key)
        if cached:
            return cached

    service = BlogService(db)
    result = service.list_posts(
        featured=featured, category=category, tag=tag,
        search=search, page=page, per_page=per_page
    )

    if not search:
        cache_set(cache_key, result, 120)

    return result


@router.get("/{slug}", response_model=PostDetail)
def get_post(slug: str, db: DBSession):
    service = BlogService(db)
    post = service.get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
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
