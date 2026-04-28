from datetime import datetime

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str | None = None
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: int | None = None


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
