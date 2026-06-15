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


def comment_to_read(c, include_replies: bool = False, _depth: int = 0) -> CommentRead:
    data = {
        "id": c.id,
        "content": c.content,
        "post_id": c.post_id,
        "user_id": c.user_id,
        "parent_id": c.parent_id,
        "is_approved": c.is_approved,
        "created_at": c.created_at,
        "author_name": c.author.username if c.author else None,
        "replies": [],
    }
    cr = CommentRead.model_validate(data)
    if include_replies and c.replies and _depth < 3:
        cr.replies = [comment_to_read(r, include_replies=True, _depth=_depth + 1) for r in c.replies if r.id != c.id]
    return cr
