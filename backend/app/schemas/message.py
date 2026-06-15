from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MessageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=120)
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: int | None = None
    captcha_answer: int | None = None


class PublicMessageRead(BaseModel):
    id: int
    name: str
    content: str
    color: str
    parent_id: int | None = None
    admin_reply: str | None = None
    admin_reply_at: datetime | None = None
    created_at: datetime
    replies: list["PublicMessageRead"] = []

    model_config = {"from_attributes": True}


class MessageRead(BaseModel):
    id: int
    name: str
    email: str | None = None
    content: str
    color: str
    parent_id: int | None = None
    admin_reply: str | None = None
    admin_reply_at: datetime | None = None
    created_at: datetime
    replies: list["MessageRead"] = []

    model_config = {"from_attributes": True}


class AdminReplyCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


def public_message_to_read(m, include_replies: bool = False, _depth: int = 0) -> PublicMessageRead:
    data = {
        "id": m.id,
        "name": m.name,
        "content": m.content,
        "color": m.color,
        "parent_id": m.parent_id,
        "admin_reply": m.admin_reply,
        "admin_reply_at": m.admin_reply_at,
        "created_at": m.created_at,
        "replies": [],
    }
    mr = PublicMessageRead.model_validate(data)
    if include_replies and m.replies and _depth < 3:
        mr.replies = [public_message_to_read(r, include_replies=True, _depth=_depth + 1) for r in m.replies if r.id != m.id]
    return mr


def message_to_read(m, include_replies: bool = False, _depth: int = 0) -> MessageRead:
    data = {
        "id": m.id,
        "name": m.name,
        "email": m.email,
        "content": m.content,
        "color": m.color,
        "parent_id": m.parent_id,
        "admin_reply": m.admin_reply,
        "admin_reply_at": m.admin_reply_at,
        "created_at": m.created_at,
        "replies": [],
    }
    mr = MessageRead.model_validate(data)
    if include_replies and m.replies and _depth < 3:
        mr.replies = [message_to_read(r, include_replies=True, _depth=_depth + 1) for r in m.replies if r.id != m.id]
    return mr
