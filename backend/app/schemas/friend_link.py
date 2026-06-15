from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FriendLinkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    avatar: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=255)
    category: str = Field(default="default", max_length=50)
    badge: str | None = Field(default=None, max_length=50)
    sort_order: int = 0
    is_active: bool = True

    @field_validator('url')
    @classmethod
    def url_must_be_safe(cls, v: str) -> str:
        if v.strip().lower().startswith(('javascript:', 'data:', 'vbscript:')):
            raise ValueError('URL must not use javascript:, data:, or vbscript: protocol')
        if not v.strip().lower().startswith(('http://', 'https://', '/')):
            raise ValueError('URL must start with http://, https://, or /')
        return v


class FriendLinkCreate(FriendLinkBase):
    pass


class FriendLinkUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    url: str | None = Field(default=None, min_length=1, max_length=500)
    avatar: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=50)
    badge: str | None = Field(default=None, max_length=50)
    sort_order: int | None = None
    is_active: bool | None = None

    @field_validator('url')
    @classmethod
    def url_must_be_safe(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v.strip().lower().startswith(('javascript:', 'data:', 'vbscript:')):
            raise ValueError('URL must not use javascript:, data:, or vbscript: protocol')
        if not v.strip().lower().startswith(('http://', 'https://', '/')):
            raise ValueError('URL must start with http://, https://, or /')
        return v


class FriendLinkRead(FriendLinkBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
