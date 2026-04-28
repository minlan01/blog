from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    post_id: int
    parent_id: int | None = None


class CommentRead(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int | None = None
    parent_id: int | None = None
    is_approved: bool = True
    created_at: datetime
    author_name: str | None = None
    replies: list["CommentRead"] = []

    model_config = {"from_attributes": True}

    @field_validator("replies", mode="before")
    @classmethod
    def coerce_replies(cls, v):
        if v is None:
            return []
        return v
