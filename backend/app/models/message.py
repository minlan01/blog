from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#818cf8")
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    admin_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_reply_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Self-referential: parent message's replies = all messages whose parent_id == this message's id
    replies: Mapped[list["Message"]] = relationship(
        "Message",
        backref="parent",
        primaryjoin="Message.id == foreign(remote(Message.parent_id))",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
