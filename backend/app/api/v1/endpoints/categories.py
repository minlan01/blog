from fastapi import APIRouter

from app.api.v1.deps import DBSession
from app.schemas.category import CategoryRead
from app.services.blog_service import BlogService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(db: DBSession):
    service = BlogService(db)
    return service.list_categories()
