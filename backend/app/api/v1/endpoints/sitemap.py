from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy import select

from app.api.v1.deps import DBSession
from app.core.xml_utils import xml_escape
from app.models.post import Post

router = APIRouter(tags=["seo"])


@router.get("/sitemap.xml")
def get_sitemap(db: DBSession):
    posts = list(
        db.scalars(
            select(Post)
            .where(Post.status == "published")
            .order_by(Post.published_at.desc())
        )
        .all()
    )

    static_pages = [
        {"loc": "/", "changefreq": "daily", "priority": "1.0"},
        {"loc": "/posts", "changefreq": "daily", "priority": "0.9"},
        {"loc": "/about", "changefreq": "monthly", "priority": "0.7"},
        {"loc": "/archive", "changefreq": "weekly", "priority": "0.6"},
        {"loc": "/link", "changefreq": "monthly", "priority": "0.5"},
        {"loc": "/message-board", "changefreq": "weekly", "priority": "0.5"},
    ]

    urls_xml = ""
    for page in static_pages:
        urls_xml += f"""
  <url>
    <loc>{xml_escape(page["loc"])}</loc>
    <changefreq>{page["changefreq"]}</changefreq>
    <priority>{page["priority"]}</priority>
  </url>"""

    for post in posts:
        lastmod = post.published_at.strftime("%Y-%m-%d") if post.published_at else ""
        urls_xml += f"""
  <url>
    <loc>/posts/{xml_escape(post.slug)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls_xml}
</urlset>"""
    return Response(content=xml, media_type="application/xml")
