from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.category import CategoryRead
from app.schemas.tag import TagRead


class PostSummary(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    cover_image: str | None = None
    reading_time: str
    published_at: datetime
    is_featured: bool
    view_count: int = 0
    status: str = "published"
    category: CategoryRead | None = None
    tags: list[TagRead] = []

    model_config = {"from_attributes": True}


class PostDetail(PostSummary):
    content_markdown: str


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1, max_length=500)
    content_markdown: str = Field(..., min_length=1)
    cover_image: str | None = None
    reading_time: str = "5 min"
    is_featured: bool = False
    category_id: int | None = None
    tag_ids: list[int] = []
    status: str = "published"


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, min_length=1, max_length=500)
    content_markdown: str | None = None
    cover_image: str | None = None
    reading_time: str | None = None
    is_featured: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None
    status: str | None = None
