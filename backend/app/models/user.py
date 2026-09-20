from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    refresh_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_memory: Mapped[str | None] = mapped_column(Text, nullable=True)
    # token 版本号：改密/重置密码时递增，使所有已签发的 access_token 立即失效
    token_version: Mapped[int] = mapped_column(Integer, default=0)

    comments = relationship("Comment", back_populates="author")
    access_tokens = relationship("AccessToken", back_populates="user")
