import os
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    storage_backend: Mapped[str] = mapped_column(String(32), default="local")
    media_type: Mapped[str] = mapped_column(String(20), default="image")
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    @property
    def stored_path(self) -> str:
        if self.file_path:
            return os.path.join("uploads", "images", self.file_path)
        return ""
