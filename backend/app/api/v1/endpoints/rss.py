from fastapi import APIRouter, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession
from app.models.post import Post
from app.models.site_config import SiteConfig

router = APIRouter(tags=["rss"])


@router.get("/rss")
def get_rss_feed(db: DBSession, limit: int = Query(default=20, ge=1, le=50)):
    site = db.scalar(select(SiteConfig).limit(1))
    site_name = site.site_name if site else "My Blog"
    site_desc = site.intro_text if site else ""

    posts = list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .order_by(Post.published_at.desc())
            .limit(limit)
        )
        .unique()
        .all()
    )

    items_xml = ""
    for post in posts:
        pub_date = post.published_at.strftime("%a, %d %b %Y %H:%M:%S GMT") if post.published_at else ""
        link = f"/posts/{post.slug}"
        items_xml += f"""
    <item>
      <title>{_escape(post.title)}</title>
      <link>{link}</link>
      <description>{_escape(post.summary)}</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{link}</guid>
    </item>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{_escape(site_name)}</title>
    <description>{_escape(site_desc)}</description>
    <link>/</link>
    <atom:link href="/api/v1/rss" rel="self" type="application/rss+xml"/>
    <language>zh-CN</language>{items_xml}
  </channel>
</rss>"""
    return Response(content=xml, media_type="application/xml")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
