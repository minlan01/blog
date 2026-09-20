from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AccessToken(Base):
    """Personal Access Token — 用于 AI/脚本调 API（发文章、上传媒体等）"""
    __tablename__ = "access_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 令牌哈希（SHA-256），明文只在创建时返回一次
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    # 权限范围，逗号分隔：posts:create,upload 或 *
    scopes: Mapped[str] = mapped_column(String(200), default="*")
    # 过期时间（null = 永不过期）
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    # 撤销标记
    revoked: Mapped[bool] = mapped_column(default=False)

    user = relationship("User", back_populates="access_tokens")
