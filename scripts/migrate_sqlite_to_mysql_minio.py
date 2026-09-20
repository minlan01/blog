from __future__ import annotations

import argparse
import mimetypes
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_container_secret() -> None:
    if os.environ.get("SECRET_KEY"):
        return
    secret_file = Path("/app/data/.secret_key")
    if secret_file.is_file():
        os.environ["SECRET_KEY"] = secret_file.read_text(encoding="utf-8").strip()


_load_container_secret()

from sqlalchemy import text  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.friend_link import FriendLink  # noqa: E402
from app.models.image import Image  # noqa: E402
from app.models.message import Message  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.post_revision import PostRevision  # noqa: E402
from app.models.site_config import SiteConfig  # noqa: E402
from app.models.tag import Tag  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.object_storage import storage  # noqa: E402


TABLES = [
    "post_tags",
    "post_revisions",
    "comments",
    "messages",
    "posts",
    "friend_links",
    "tags",
    "categories",
    "site_configs",
    "users",
    "images",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    return bool(value)


def _as_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    text_value = str(value).strip()
    try:
        return datetime.fromisoformat(text_value)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text_value, fmt)
        except ValueError:
            continue
    return None


def _rows(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f'SELECT * FROM "{table}"'))


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    return any(row["name"] == column for row in conn.execute(f'PRAGMA table_info("{table}")'))


def _make_object_key(media_type: str, image_id: int, filename: str, created_at: datetime | None) -> str:
    when = created_at or _utc_now()
    folder = "videos" if media_type == "video" else "images"
    return f"{folder}/{when:%Y/%m}/legacy-{image_id}-{filename}"


def _find_local_file(uploads_dir: Path, file_path: str | None, filename: str) -> Path | None:
    candidates: list[Path] = []
    if file_path:
        candidates.extend(
            [
                uploads_dir / file_path,
                uploads_dir / "images" / file_path,
                uploads_dir / "uploads" / "images" / file_path,
            ]
        )
    candidates.extend(
        [
            uploads_dir / filename,
            uploads_dir / "images" / filename,
            uploads_dir / "uploads" / "images" / filename,
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _guess_media_type(mime_type: str) -> str:
    return "video" if mime_type.startswith("video/") else "image"


def _clear_target(db) -> None:
    db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    for table in TABLES:
        db.execute(text(f"DELETE FROM {table}"))
    db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.commit()


def _reset_auto_increment(db) -> None:
    for table in reversed(TABLES):
        if table == "post_tags":
            continue
        db.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
    db.commit()


def _copy_basic_rows(conn: sqlite3.Connection, db) -> dict[str, int]:
    counts: dict[str, int] = {}

    users = []
    for row in _rows(conn, "users"):
        users.append(
            User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                password_hash=row["password_hash"],
                role=row["role"],
                bio=row["bio"],
                avatar=row["avatar"],
                created_at=_as_dt(row["created_at"]) or _utc_now(),
                refresh_token=row["refresh_token"] if "refresh_token" in row.keys() else None,
                failed_login_attempts=row["failed_login_attempts"]
                if "failed_login_attempts" in row.keys()
                else 0,
                locked_until=_as_dt(row["locked_until"]) if "locked_until" in row.keys() else None,
                email_verified=_as_bool(row["email_verified"]) if "email_verified" in row.keys() else False,
            )
        )
    db.add_all(users)
    counts["users"] = len(users)

    categories = [
        Category(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            description=row["description"],
        )
        for row in _rows(conn, "categories")
    ]
    db.add_all(categories)
    counts["categories"] = len(categories)

    tags = [
        Tag(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
        )
        for row in _rows(conn, "tags")
    ]
    db.add_all(tags)
    counts["tags"] = len(tags)

    site_configs = [
        SiteConfig(
            id=row["id"],
            site_name=row["site_name"],
            hero_title=row["hero_title"],
            hero_subtitle=row["hero_subtitle"],
            intro_text=row["intro_text"],
            avatar=row["avatar"],
            email=row["email"],
            github_url=row["github_url"],
            location=row["location"],
            icp_filing=row["icp_filing"] if "icp_filing" in row.keys() else "",
            icp_link=row["icp_link"] if "icp_link" in row.keys() else "",
        )
        for row in _rows(conn, "site_configs")
    ]
    db.add_all(site_configs)
    counts["site_configs"] = len(site_configs)

    posts = []
    for row in _rows(conn, "posts"):
        posts.append(
            Post(
                id=row["id"],
                title=row["title"],
                slug=row["slug"],
                summary=row["summary"],
                cover_image=row["cover_image"],
                content_markdown=row["content_markdown"],
                reading_time=row["reading_time"],
                is_featured=_as_bool(row["is_featured"]),
                published_at=_as_dt(row["published_at"]) or _utc_now(),
                updated_at=_as_dt(row["updated_at"]) if "updated_at" in row.keys() else None,
                category_id=row["category_id"],
                view_count=row["view_count"] if "view_count" in row.keys() else 0,
                status=row["status"] if "status" in row.keys() else "published",
            )
        )
    db.add_all(posts)
    counts["posts"] = len(posts)

    friend_links = [
        FriendLink(
            id=row["id"],
            name=row["name"],
            url=row["url"],
            avatar=row["avatar"],
            description=row["description"],
            category=row["category"],
            badge=row["badge"],
            sort_order=row["sort_order"],
            is_active=_as_bool(row["is_active"], True),
            created_at=_as_dt(row["created_at"]) or _utc_now(),
        )
        for row in _rows(conn, "friend_links")
    ]
    db.add_all(friend_links)
    counts["friend_links"] = len(friend_links)

    db.flush()

    comments = []
    for row in _rows(conn, "comments"):
        comments.append(
            Comment(
                id=row["id"],
                content=row["content"],
                post_id=row["post_id"],
                user_id=row["user_id"],
                parent_id=row["parent_id"] if "parent_id" in row.keys() else None,
                is_approved=_as_bool(row["is_approved"], True)
                if "is_approved" in row.keys()
                else True,
                created_at=_as_dt(row["created_at"]) or _utc_now(),
                updated_at=_as_dt(row["updated_at"]) if "updated_at" in row.keys() else None,
            )
        )
    db.add_all(comments)
    counts["comments"] = len(comments)

    messages = []
    for row in _rows(conn, "messages"):
        messages.append(
            Message(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                content=row["content"],
                color=row["color"],
                parent_id=row["parent_id"] if "parent_id" in row.keys() else None,
                admin_reply=row["admin_reply"] if "admin_reply" in row.keys() else None,
                admin_reply_at=_as_dt(row["admin_reply_at"]) if "admin_reply_at" in row.keys() else None,
                created_at=_as_dt(row["created_at"]) or _utc_now(),
            )
        )
    db.add_all(messages)
    counts["messages"] = len(messages)

    revisions = []
    if "post_revisions" in [r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
        for row in _rows(conn, "post_revisions"):
            revisions.append(
                PostRevision(
                    id=row["id"],
                    post_id=row["post_id"],
                    title=row["title"],
                    content_markdown=row["content_markdown"],
                    summary=row["summary"],
                    version_number=row["version_number"],
                    created_at=_as_dt(row["created_at"]) or _utc_now(),
                )
            )
    db.add_all(revisions)
    counts["post_revisions"] = len(revisions)

    db.flush()

    post_tags = _rows(conn, "post_tags")
    for row in post_tags:
        db.execute(
            text("INSERT INTO post_tags (post_id, tag_id) VALUES (:post_id, :tag_id)"),
            {"post_id": row["post_id"], "tag_id": row["tag_id"]},
        )
    counts["post_tags"] = len(post_tags)

    return counts


def _copy_images(conn: sqlite3.Connection, db, uploads_dir: Path, dry_run: bool) -> tuple[int, list[str]]:
    warnings: list[str] = []
    images = _rows(conn, "images")
    has_file_path = _has_column(conn, "images", "file_path")
    for row in images:
        filename = row["filename"]
        mime_type = row["mime_type"]
        created_at = _as_dt(row["created_at"]) or _utc_now()
        file_path = row["file_path"] if has_file_path else None
        data = row["data"] if "data" in row.keys() else None
        source_file = _find_local_file(uploads_dir, file_path, filename)

        size = row["size"] or 0
        object_key = None
        storage_backend = "local"
        media_type = _guess_media_type(mime_type)

        if settings.use_minio:
            payload_source: Path | None = source_file
            if payload_source is not None:
                size = payload_source.stat().st_size
                guessed_mime, _ = mimetypes.guess_type(payload_source.name)
                mime_type = mime_type or guessed_mime or "application/octet-stream"
                object_key = _make_object_key(media_type, row["id"], filename, created_at)
                if not dry_run:
                    with payload_source.open("rb") as handle:
                        storage.put_file(object_key, handle, size, mime_type)
                storage_backend = "minio"
                file_path = None
                data = None
            elif data:
                size = len(data)
                object_key = _make_object_key(media_type, row["id"], filename, created_at)
                if not dry_run:
                    from io import BytesIO

                    storage.put_file(object_key, BytesIO(data), size, mime_type)
                storage_backend = "minio"
                file_path = None
                data = None
            else:
                warnings.append(f"image {row['id']} ({filename}) has no source file or blob")

        db.add(
            Image(
                id=row["id"],
                filename=filename,
                mime_type=mime_type,
                data=data,
                file_path=file_path,
                object_key=object_key,
                storage_backend=storage_backend,
                media_type=media_type,
                size=size,
                created_at=created_at,
            )
        )

    return len(images), warnings


def migrate(sqlite_db: Path, uploads_dir: Path, dry_run: bool = False) -> int:
    if not sqlite_db.is_file():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_db}")
    if not uploads_dir.exists():
        raise FileNotFoundError(f"Uploads directory not found: {uploads_dir}")
    if settings.DATABASE_BACKEND.lower() != "mysql":
        raise RuntimeError(f"Target database must be MySQL, got {settings.DATABASE_BACKEND!r}")

    conn = sqlite3.connect(sqlite_db)
    conn.row_factory = sqlite3.Row

    if dry_run:
        print("Dry run: no target data will be changed.")
        table_names = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in TABLES:
            if table in table_names:
                count = conn.execute(f'SELECT COUNT(*) AS count FROM "{table}"').fetchone()["count"]
                print(f"{table}: {count}")
        for row in _rows(conn, "images"):
            source_file = _find_local_file(
                uploads_dir,
                row["file_path"] if "file_path" in row.keys() else None,
                row["filename"],
            )
            blob = row["data"] if "data" in row.keys() else None
            if source_file:
                print(f"image {row['id']}: {source_file} -> minio")
            elif blob:
                print(f"image {row['id']}: blob {len(blob)} bytes -> minio")
            else:
                print(f"WARNING: image {row['id']} ({row['filename']}) has no source file or blob")
        conn.close()
        return 0

    with SessionLocal() as db:
        _clear_target(db)
        _reset_auto_increment(db)

        counts = _copy_basic_rows(conn, db)
        image_count, warnings = _copy_images(conn, db, uploads_dir, dry_run=False)
        counts["images"] = image_count

        db.commit()
        _reset_auto_increment(db)

    conn.close()

    for table, count in counts.items():
        print(f"{table}: {count}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy SQLite blog data to MySQL and MinIO.")
    parser.add_argument("--sqlite-db", required=True, type=Path)
    parser.add_argument("--uploads-dir", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return migrate(args.sqlite_db, args.uploads_dir, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
