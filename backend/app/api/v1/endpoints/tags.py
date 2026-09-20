from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.v1.deps import DBSession
from app.models.post import Post, post_tags
from app.models.tag import Tag
from app.schemas.tag import TagRead
from app.services.blog_service import BlogService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: DBSession):
    service = BlogService(db)
    return service.list_tags()


@router.get("/cloud")
def list_tags_with_count(db: DBSession):
    """标签云：返回每个标签关联的已发布文章数"""
    stmt = (
        select(
            Tag.id,
            Tag.name,
            Tag.slug,
            func.count(post_tags.c.post_id).label("post_count"),
        )
        .join(post_tags, post_tags.c.tag_id == Tag.id)
        .join(Post, Post.id == post_tags.c.post_id)
        .where(Post.status == "published")
        .group_by(Tag.id)
        .order_by(func.count(post_tags.c.post_id).desc())
    )
    rows = db.execute(stmt).all()
    return [
        {"id": r.id, "name": r.name, "slug": r.slug, "post_count": r.post_count}
        for r in rows
    ]
