from fastapi import APIRouter, HTTPException

from app.api.v1.deps import DBSession
from app.schemas.site import SiteProfile
from app.services.blog_service import BlogService

router = APIRouter(prefix="/site", tags=["site"])


@router.get("/profile", response_model=SiteProfile)
def get_site_profile(db: DBSession):
    service = BlogService(db)
    profile = service.get_site_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Site profile not found")
    return profile
