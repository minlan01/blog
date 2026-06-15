from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Table, Text, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    reading_time: Mapped[str] = mapped_column(String(32), default="5 min")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="published", index=True)

    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    revisions = relationship("PostRevision", back_populates="post", cascade="all, delete-orphan")
