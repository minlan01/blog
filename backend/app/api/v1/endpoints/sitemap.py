from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy import select

from app.api.v1.deps import DBSession
from app.core.config import settings
from app.core.xml_utils import xml_escape
from app.models.post import Post

router = APIRouter(tags=["seo"])


@router.get("/sitemap.xml")
def get_sitemap(db: DBSession):
    site_url = settings.SITE_URL.rstrip("/")

    posts = list(
        db.scalars(
            select(Post)
            .where(Post.status == "published")
            .order_by(Post.published_at.desc())
        )
        .all()
    )

    static_pages = [
        {"path": "/", "changefreq": "daily", "priority": "1.0"},
        {"path": "/posts", "changefreq": "daily", "priority": "0.9"},
        {"path": "/about", "changefreq": "monthly", "priority": "0.7"},
        {"path": "/archive", "changefreq": "weekly", "priority": "0.6"},
        {"path": "/link", "changefreq": "monthly", "priority": "0.5"},
        {"path": "/message-board", "changefreq": "weekly", "priority": "0.5"},
    ]

    urls_xml = ""
    for page in static_pages:
        loc = f"{site_url}{page['path']}"
        urls_xml += f"""
  <url>
    <loc>{xml_escape(loc)}</loc>
    <changefreq>{page["changefreq"]}</changefreq>
    <priority>{page["priority"]}</priority>
  </url>"""

    for post in posts:
        lastmod = post.published_at.strftime("%Y-%m-%d") if post.published_at else ""
        loc = f"{site_url}/posts/{post.slug}"
        urls_xml += f"""
  <url>
    <loc>{xml_escape(loc)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls_xml}
</urlset>"""
    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/robots.txt")
def get_robots():
    site_url = settings.SITE_URL.rstrip("/")
    content = f"""User-Agent: *
Disallow: /admin
Disallow: /api/
Sitemap: {site_url}/api/v1/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
