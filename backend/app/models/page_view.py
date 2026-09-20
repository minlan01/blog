from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PageView(Base):
    """访问记录 — 轻量统计系统"""
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    # 设备类型：desktop / mobile / tablet / bot
    device: Mapped[str] = mapped_column(String(20), default="desktop")
    # 浏览器：chrome / safari / firefox / edge / other
    browser: Mapped[str] = mapped_column(String(20), default="other")
    # 来源：直接/搜索引擎/外链域名
    referrer_source: Mapped[str] = mapped_column(String(100), default="direct")
    # 访客 IP 哈希（只存前 8 位 md5，不可逆，用于去重不用于追踪）
    ip_hash: Mapped[str] = mapped_column(String(8), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    __table_args__ = (
        Index("ix_page_views_path_created", "path", "created_at"),
    )
