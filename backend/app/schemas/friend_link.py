from datetime import datetime

from pydantic import BaseModel


class FriendLinkBase(BaseModel):
    name: str
    url: str
    avatar: str | None = None
    description: str | None = None
    category: str = "default"
    badge: str | None = None
    sort_order: int = 0
    is_active: bool = True


class FriendLinkCreate(FriendLinkBase):
    pass


class FriendLinkUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    avatar: str | None = None
    description: str | None = None
    category: str | None = None
    badge: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class FriendLinkRead(FriendLinkBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
