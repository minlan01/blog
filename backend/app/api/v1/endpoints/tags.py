from fastapi import APIRouter

from app.api.v1.deps import DBSession
from app.schemas.tag import TagRead
from app.services.blog_service import BlogService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: DBSession):
    service = BlogService(db)
    return service.list_tags()
