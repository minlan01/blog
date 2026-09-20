"""OG share image generator.

Generates 1200x630 PNG images for social media sharing (og:image).
Uses Pillow to composite post title, category, and site branding.

Output is cached on disk (data/og_cache/) to avoid re-rendering.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from app.models.post import Post

logger = logging.getLogger("blog")

# ── Constants ──
WIDTH = 1200
HEIGHT = 630
CACHE_DIR = Path(os.environ.get("OG_CACHE_DIR", "data/og_cache"))

# Theme colors (dark glass aesthetic matching the blog)
BG_TOP = (15, 15, 30)         # #0f0f1e
BG_BOTTOM = (25, 20, 45)      # #19142d
ACCENT_INDIGO = (129, 140, 248)  # #818cf8
ACCENT_AMBER = (245, 158, 11)    # #f59e0b
TEXT_PRIMARY = (240, 240, 250)
TEXT_SECONDARY = (160, 160, 180)

# Font search paths (tries multiple common locations)
FONT_SEARCH = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",      # Linux (Docker)
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",       # Linux CJK
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",       # Alpine
    "C:\\Windows\\Fonts\\msyhbd.ttc",                              # Windows 微软雅黑
    "C:\\Windows\\Fonts\\simhei.ttf",                              # Windows 黑体
    "/System/Library/Fonts/PingFang.ttc",                         # macOS
]

FONT_MONO_SEARCH = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "C:\\Windows\\Fonts\\consola.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def _find_font(search_paths: list[str]) -> str | None:
    for p in search_paths:
        if os.path.exists(p):
            return p
    return None


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    path = _find_font(FONT_SEARCH)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _get_mono_font(size: int) -> ImageFont.FreeTypeFont:
    path = _find_font(FONT_MONO_SEARCH)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    lines: list[str] = []
    current = ""
    for char in text:
        test = current + char
        try:
            bbox = font.getbbox(test)
            w = bbox[2] - bbox[0]
        except Exception:
            w = len(test) * 20
        if w > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines[:3]  # max 3 lines


def _hash_cache_key(post_id: int, title: str) -> str:
    raw = f"{post_id}:{title}"
    return hashlib.md5(raw.encode()).hexdigest()


def generate_og_image(post: "Post", site_name: str = "Blog") -> bytes:
    """Generate a 1200x630 OG image for a post. Returns PNG bytes.

    Results are cached on disk by (post_id, title) hash.
    """
    # Check cache
    cache_key = _hash_cache_key(post.id, post.title)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{cache_key}.png"

    if cache_path.exists():
        return cache_path.read_bytes()

    # Create canvas
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient background (top to bottom)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Decorative accent bar (left side)
    draw.rectangle([0, 0, 6, HEIGHT], fill=ACCENT_INDIGO)

    # Category label (top)
    category_name = ""
    if hasattr(post, "category") and post.category:
        category_name = post.category.name or ""
    if category_name:
        cat_font = _get_mono_font(22)
        draw.text((80, 70), category_name.upper(), font=cat_font, fill=ACCENT_AMBER)

    # Title (center, wrapped)
    title_font = _get_font(56)
    title_lines = _wrap_text(post.title or "Untitled", title_font, WIDTH - 160)
    title_y = 160
    for line in title_lines:
        draw.text((80, title_y), line, font=title_font, fill=TEXT_PRIMARY)
        title_y += 70

    # Summary (below title, truncated)
    summary = (post.summary or "")[:120]
    if summary:
        summary_font = _get_font(26)
        summary_lines = _wrap_text(summary, summary_font, WIDTH - 160)
        sum_y = title_y + 30
        for line in summary_lines[:2]:
            draw.text((80, sum_y), line, font=summary_font, fill=TEXT_SECONDARY)
            sum_y += 38

    # Site name (bottom right)
    site_font = _get_mono_font(24)
    site_text = f"— {site_name}"
    try:
        bbox = site_font.getbbox(site_text)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 200
    draw.text((WIDTH - tw - 80, HEIGHT - 60), site_text, font=site_font, fill=TEXT_SECONDARY)

    # Subtle grid pattern overlay (cyberpunk touch)
    for x in range(0, WIDTH, 40):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 3), width=1)
    for y in range(0, HEIGHT, 40):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 3), width=1)

    # Save to cache
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()

    try:
        cache_path.write_bytes(png_bytes)
    except Exception as e:
        logger.warning("Failed to cache OG image: %s", e)

    return png_bytes
