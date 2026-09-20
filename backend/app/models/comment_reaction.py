from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CommentReaction(Base):
    __tablename__ = "comment_reactions"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "emoji", name="uq_comment_reaction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emoji: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
