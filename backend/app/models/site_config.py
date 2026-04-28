from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hero_title: Mapped[str] = mapped_column(String(255), nullable=False)
    hero_subtitle: Mapped[str] = mapped_column(String(255), nullable=False)
    intro_text: Mapped[str] = mapped_column(Text, nullable=False)
    avatar: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    github_url: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    icp_filing: Mapped[str] = mapped_column(String(120), default="")
    icp_link: Mapped[str] = mapped_column(String(255), default="")
