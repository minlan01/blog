from fastapi import APIRouter, HTTPException

from app.api.v1.deps import DBSession, SuperAdmin
from app.models.friend_link import FriendLink
from app.schemas.friend_link import FriendLinkCreate, FriendLinkRead, FriendLinkUpdate
from sqlalchemy import select

router = APIRouter()


# ── Public ──


@router.get("/friend-links", response_model=list[FriendLinkRead])
def list_friend_links(db: DBSession):
    stmt = (
        select(FriendLink)
        .where(FriendLink.is_active.is_(True))
        .order_by(FriendLink.sort_order.asc(), FriendLink.created_at.desc())
    )
    return list(db.scalars(stmt).all())


# ── Admin ──


_WRITABLE_FIELDS = {"name", "url", "avatar", "description", "category", "badge", "sort_order", "is_active"}


@router.post("/admin/friend-links", response_model=FriendLinkRead)
def create_friend_link(data: FriendLinkCreate, db: DBSession, _admin: SuperAdmin):
    safe_data = {k: v for k, v in data.model_dump().items() if k in _WRITABLE_FIELDS}
    link = FriendLink(**safe_data)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.put("/admin/friend-links/{link_id}", response_model=FriendLinkRead)
def update_friend_link(link_id: int, data: FriendLinkUpdate, db: DBSession, _admin: SuperAdmin):
    link = db.get(FriendLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Friend link not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key in _WRITABLE_FIELDS:
            setattr(link, key, value)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/admin/friend-links/{link_id}", status_code=204)
def delete_friend_link(link_id: int, db: DBSession, _admin: SuperAdmin):
    link = db.get(FriendLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Friend link not found")
    db.delete(link)
    db.commit()
