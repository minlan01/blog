from fastapi import APIRouter, HTTPException, Query

from app.api.v1.deps import DBSession
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
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=50),
):
    service = BlogService(db)
    return service.list_posts(
        featured=featured, category=category, tag=tag,
        search=search, page=page, per_page=per_page
    )


@router.get("/{slug}", response_model=PostDetail)
def get_post(slug: str, db: DBSession):
    service = BlogService(db)
    post = service.get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # Increment view count
    post.view_count = (post.view_count or 0) + 1
    db.commit()
    return post


@router.get("/{slug}/related", response_model=list[PostSummary])
def get_related_posts(slug: str, db: DBSession, limit: int = Query(default=4, ge=1, le=10)):
    service = BlogService(db)
    post = service.get_post_by_slug(slug, published_only=True)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return service.get_related_posts(post.id, limit)
