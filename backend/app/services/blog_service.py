from datetime import datetime, timezone
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.cache import cache_delete, cache_get, cache_set
from app.models import Category, Post, SiteConfig, Tag
from app.models.post_revision import PostRevision
from app.models.post import post_tags


class BlogService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _calc_reading_time(content: str) -> str:
        cjk_chars = len(re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', content))
        en_words = len(re.findall(r'[a-zA-Z]+', content))
        minutes = max(1, round(max(cjk_chars / 300, en_words / 200)))
        return f"{minutes} min"

    # ────────────── Site ──────────────

    def get_site_profile(self) -> SiteConfig | None:
        cached = cache_get("site:profile")
        if cached:
            return cached
        result = self.db.scalar(select(SiteConfig).limit(1))
        if result:
            cache_set("site:profile", result, 600)  # 10 min
        return result

    _SITE_WRITABLE_FIELDS = {
        "site_name", "hero_title", "hero_subtitle", "intro_text",
        "avatar", "email", "github_url", "location", "icp_filing", "icp_link",
    }

    _CATEGORY_WRITABLE_FIELDS = {"name", "slug", "description"}

    _TAG_WRITABLE_FIELDS = {"name", "slug", "description"}

    def update_site_profile(self, data: dict) -> SiteConfig | None:
        profile = self.get_site_profile()
        if not profile:
            return None
        for key, value in data.items():
            if key in self._SITE_WRITABLE_FIELDS and value is not None:
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        cache_delete("site:profile")
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
            search = search[:100]
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

        content = data.get("content_markdown", "")
        reading_time = data.get("reading_time", self._calc_reading_time(content))

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
        self._save_revision(post)
        self.db.commit()
        self.db.refresh(post)
        cache_delete("posts:")
        cache_delete("stats:")
        return self.get_post_by_id(post.id)  # type: ignore[return-value]

    _POST_WRITABLE_FIELDS = {
        "title", "slug", "summary", "content_markdown", "cover_image",
        "reading_time", "is_featured", "category_id", "status", "published_at",
    }

    def update_post(self, post_id: int, data: dict, tag_ids: list[int] | None = None) -> Post | None:
        post = self.db.get(Post, post_id)
        if not post:
            return None

        self._save_revision(post)

        for key, value in data.items():
            if key in self._POST_WRITABLE_FIELDS and value is not None:
                setattr(post, key, value)
        if tag_ids is not None:
            post.tags = list(self.db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all())
        # When publishing a draft, set published_at to now
        if data.get("status") == "published" and post.published_at is None:
            post.published_at = datetime.now(timezone.utc)

        if post.content_markdown:
            post.reading_time = self._calc_reading_time(post.content_markdown)

        self.db.commit()
        cache_delete("posts:")
        cache_delete("stats:")
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
        from app.models.post_revision import PostRevision
        post = self.db.get(Post, post_id)
        if not post:
            return False
        self.db.query(Comment).filter(Comment.post_id == post_id).delete()
        self.db.query(PostRevision).filter(PostRevision.post_id == post_id).delete()
        self.db.delete(post)
        self.db.commit()
        cache_delete("posts:")
        cache_delete("stats:")
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
        safe_data = {k: v for k, v in data.items() if k in self._CATEGORY_WRITABLE_FIELDS}
        cat = Category(**safe_data)
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
            if key in self._CATEGORY_WRITABLE_FIELDS and value is not None:
                setattr(cat, key, value)
        self.db.commit()
        self.db.refresh(cat)
        cache_delete("categories:")
        return cat

    def delete_category(self, cat_id: int) -> bool:
        cat = self.db.get(Category, cat_id)
        if not cat:
            return False
        from app.models.post import Post
        self.db.query(Post).filter(Post.category_id == cat_id).update(
            {Post.category_id: None}, synchronize_session=False
        )
        self.db.delete(cat)
        self.db.commit()
        cache_delete("categories:")
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
        safe_data = {k: v for k, v in data.items() if k in self._TAG_WRITABLE_FIELDS}
        tag = Tag(**safe_data)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        cache_delete("tags:all")
        return tag

    def update_tag(self, tag_id: int, data: dict) -> Tag | None:
        tag = self.db.get(Tag, tag_id)
        if not tag:
            return None
        for key, value in data.items():
            if key in self._TAG_WRITABLE_FIELDS and value is not None:
                setattr(tag, key, value)
        self.db.commit()
        self.db.refresh(tag)
        cache_delete("tags:all")
        return tag

    def delete_tag(self, tag_id: int) -> bool:
        tag = self.db.get(Tag, tag_id)
        if not tag:
            return False
        self.db.delete(tag)
        self.db.commit()
        cache_delete("tags:all")
        return True

    # ────────────── Search & Pagination ──────────────

    def search_posts(self, query: str, limit: int = 50) -> list[Post]:
        search_term = f"%{query}%"
        stmt = (
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.tags))
            .where(
                (Post.title.ilike(search_term)) | (Post.summary.ilike(search_term)),
                Post.status == "published",
            )
            .order_by(Post.published_at.desc())
            .limit(limit)
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
        descendant_ids = self._collect_comment_descendant_ids(comment_id)
        for cid in reversed(descendant_ids):
            c = self.db.get(Comment, cid)
            if c:
                self.db.delete(c)
        self.db.delete(comment)
        self.db.commit()
        return True

    def _collect_comment_descendant_ids(self, comment_id: int) -> list[int]:
        from app.models.comment import Comment
        ids: list[int] = []
        children = list(self.db.scalars(select(Comment).where(Comment.parent_id == comment_id)).all())
        for child in children:
            ids.append(child.id)
            ids.extend(self._collect_comment_descendant_ids(child.id))
        return ids
