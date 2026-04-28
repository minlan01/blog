from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.cache import cache_delete, cache_get, cache_set
from app.models import Category, Post, SiteConfig, Tag
from app.models.post_revision import PostRevision
from app.models.post import post_tags


class BlogService:
    def __init__(self, db: Session):
        self.db = db

    # ────────────── Site ──────────────

    def get_site_profile(self) -> SiteConfig | None:
        cached = cache_get("site:profile")
        if cached:
            return cached
        result = self.db.scalar(select(SiteConfig).limit(1))
        if result:
            cache_set("site:profile", result, 600)  # 10 min
        return result

    def update_site_profile(self, data: dict) -> SiteConfig | None:
        profile = self.get_site_profile()
        if not profile:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        cache_delete("site:")
        return profile

    # ────────────── Posts ──────────────

    def list_posts(
        self,
        featured: bool | None = None,
        category: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(Post.status == "published")
            .order_by(Post.published_at.desc())
        )
        if featured is True:
            stmt = stmt.where(Post.is_featured.is_(True))
        if category:
            stmt = stmt.join(Post.category).where(Category.slug == category)
        if tag:
            stmt = stmt.join(Post.tags).where(Tag.slug == tag)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                (Post.title.ilike(search_term)) | (Post.summary.ilike(search_term))
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        posts = list(self.db.scalars(stmt).unique().all())

        total_pages = (total + per_page - 1) // per_page

        return {
            "items": posts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        }

    def get_post_by_slug(self, slug: str, published_only: bool = True) -> Post | None:
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(Post.slug == slug)
        )
        if published_only:
            stmt = stmt.where(Post.status == "published")
        return self.db.scalar(stmt)

    def list_all_posts(self) -> list[Post]:
        """List all posts including drafts (admin only)."""
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .order_by(Post.published_at.desc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def get_post_by_id(self, post_id: int) -> Post | None:
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(Post.id == post_id)
        )
        return self.db.scalar(stmt)

    def create_post(self, data: dict, tag_ids: list[int]) -> Post:
        tags = list(self.db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()) if tag_ids else []

        # Auto-calculate reading time
        content = data.get("content_markdown", "")
        word_count = len(content)
        minutes = max(1, word_count // 300)
        reading_time = data.get("reading_time", f"{minutes} min")

        post = Post(
            title=data["title"],
            slug=data["slug"],
            summary=data["summary"],
            content_markdown=data["content_markdown"],
            cover_image=data.get("cover_image"),
            reading_time=reading_time,
            is_featured=data.get("is_featured", False),
            category_id=data.get("category_id"),
            status=data.get("status", "published"),
            published_at=datetime.now(timezone.utc) if data.get("status") == "published" else None,
            tags=tags,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        cache_delete("posts:")
        return self.get_post_by_id(post.id)  # type: ignore[return-value]

    def update_post(self, post_id: int, data: dict, tag_ids: list[int] | None = None) -> Post | None:
        post = self.db.get(Post, post_id)
        if not post:
            return None

        # Save revision before updating
        self._save_revision(post)

        for key, value in data.items():
            if value is not None and key != "tag_ids":
                setattr(post, key, value)
        if tag_ids is not None:
            post.tags = list(self.db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all())
        # When publishing a draft, set published_at to now
        if data.get("status") == "published" and post.published_at is None:
            post.published_at = datetime.now(timezone.utc)

        # Auto-calculate reading time
        if post.content_markdown:
            word_count = len(post.content_markdown)
            minutes = max(1, word_count // 300)
            post.reading_time = f"{minutes} min"

        self.db.commit()
        cache_delete("posts:")
        return self.get_post_by_id(post_id)

    def _save_revision(self, post: Post) -> None:
        """Save current post state as a revision."""
        # Get current max version
        max_ver = self.db.scalar(
            select(func.max(PostRevision.version_number)).where(PostRevision.post_id == post.id)
        ) or 0

        rev = PostRevision(
            post_id=post.id,
            title=post.title,
            content_markdown=post.content_markdown,
            summary=post.summary,
            version_number=max_ver + 1,
        )
        self.db.add(rev)

    def get_related_posts(self, post_id: int, limit: int = 4) -> list[Post]:
        """Get related posts based on shared category and tags."""
        post = self.db.get(Post, post_id)
        if not post:
            return []

        # Find posts sharing the same category or tags
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(Post.id != post_id, Post.status == "published")
        )

        if post.category_id:
            stmt_cat = stmt.where(Post.category_id == post.category_id)
            related = list(self.db.scalars(stmt_cat.limit(limit)).unique().all())
            if len(related) >= limit:
                return related[:limit]
        else:
            related = []

        # Fill remaining with posts sharing tags
        if post.tags:
            tag_ids = [t.id for t in post.tags]
            existing_ids = [p.id for p in related] + [post_id]
            stmt_tags = (
                stmt.join(post_tags)
                .where(post_tags.c.tag_id.in_(tag_ids), Post.id.notin_(existing_ids))
                .limit(limit - len(related))
            )
            related.extend(list(self.db.scalars(stmt_tags).unique().all()))

        return related[:limit]

    def delete_post(self, post_id: int) -> bool:
        from app.models.comment import Comment
        post = self.db.get(Post, post_id)
        if not post:
            return False
        # Delete comments first (SQLite FK constraint)
        self.db.query(Comment).filter(Comment.post_id == post_id).delete()
        self.db.delete(post)
        self.db.commit()
        cache_delete("posts:")
        return True

    # ────────────── Categories ──────────────

    def list_categories(self) -> list[Category]:
        cached = cache_get("categories:all")
        if cached:
            return cached
        result = list(self.db.scalars(select(Category).order_by(Category.name.asc())).all())
        cache_set("categories:all", result, 600)
        return result

    def create_category(self, data: dict) -> Category:
        cat = Category(**data)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        cache_delete("categories:")
        return cat

    def update_category(self, cat_id: int, data: dict) -> Category | None:
        cat = self.db.get(Category, cat_id)
        if not cat:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(cat, key, value)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def delete_category(self, cat_id: int) -> bool:
        cat = self.db.get(Category, cat_id)
        if not cat:
            return False
        self.db.delete(cat)
        self.db.commit()
        return True

    # ────────────── Tags ──────────────

    def list_tags(self) -> list[Tag]:
        cached = cache_get("tags:all")
        if cached:
            return cached
        result = list(self.db.scalars(select(Tag).order_by(Tag.name.asc())).all())
        cache_set("tags:all", result, 600)
        return result

    def create_tag(self, data: dict) -> Tag:
        tag = Tag(**data)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def update_tag(self, tag_id: int, data: dict) -> Tag | None:
        tag = self.db.get(Tag, tag_id)
        if not tag:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(tag, key, value)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete_tag(self, tag_id: int) -> bool:
        tag = self.db.get(Tag, tag_id)
        if not tag:
            return False
        self.db.delete(tag)
        self.db.commit()
        return True

    # ────────────── Search & Pagination ──────────────

    def search_posts(self, query: str) -> list[Post]:
        search_term = f"%{query}%"
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(
                (Post.title.ilike(search_term)) | (Post.summary.ilike(search_term)),
                Post.status == "published",
            )
            .order_by(Post.published_at.desc())
        )
        return list(self.db.scalars(stmt).unique().all())

    # ────────────── Comments ──────────────

    def list_comments(self, post_id: int) -> list:
        from app.models.comment import Comment
        stmt = select(Comment).where(Comment.post_id == post_id, Comment.parent_id.is_(None)).order_by(Comment.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def create_comment(self, content: str, post_id: int, user_id: int, parent_id: int | None = None):
        from app.models.comment import Comment
        comment = Comment(content=content, post_id=post_id, user_id=user_id, parent_id=parent_id)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete_comment(self, comment_id: int) -> bool:
        from app.models.comment import Comment
        comment = self.db.get(Comment, comment_id)
        if not comment:
            return False
        self.db.delete(comment)
        self.db.commit()
        return True
