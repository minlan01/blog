"""Root baseline - reflects current production schema

Revision ID: 0001_root
Revises: None
Create Date: 2026-07-26

This migration is the true baseline. It creates all core tables that were
previously created by Base.metadata.create_all() in init_db.py.
The old 3 revisions (62dbd9b622d0, a3f1c8d4e5b2, b4c2d9e8f1a0) have been
archived to _archive/ and are no longer in the migration chain.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_root"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("refresh_token", sa.String(length=500), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    # --- categories ---
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)

    # --- tags ---
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)

    # --- posts ---
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("cover_image", sa.String(length=500), nullable=True),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("reading_time", sa.String(length=32), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_posts_id"), "posts", ["id"], unique=False)
    op.create_index(op.f("ix_posts_published_at"), "posts", ["published_at"], unique=False)
    op.create_index(op.f("ix_posts_category_id"), "posts", ["category_id"], unique=False)
    op.create_index(op.f("ix_posts_status"), "posts", ["status"], unique=False)

    # --- post_tags (association table) ---
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "tag_id"),
    )

    # --- comments ---
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(op.f("ix_comments_parent_id"), "comments", ["parent_id"], unique=False)

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("admin_reply", sa.Text(), nullable=True),
        sa.Column("admin_reply_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)
    op.create_index(op.f("ix_messages_parent_id"), "messages", ["parent_id"], unique=False)

    # --- friend_links ---
    op.create_table(
        "friend_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("avatar", sa.String(length=500), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("badge", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_friend_links_id"), "friend_links", ["id"], unique=False)

    # --- images ---
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("object_key", sa.String(length=512), nullable=True),
        sa.Column("storage_backend", sa.String(length=32), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)

    # --- post_revisions ---
    op.create_table(
        "post_revisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_revisions_id"), "post_revisions", ["id"], unique=False)
    op.create_index(op.f("ix_post_revisions_post_id"), "post_revisions", ["post_id"], unique=False)

    # --- site_configs ---
    op.create_table(
        "site_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("site_name", sa.String(length=120), nullable=False),
        sa.Column("hero_title", sa.String(length=255), nullable=False),
        sa.Column("hero_subtitle", sa.String(length=255), nullable=False),
        sa.Column("intro_text", sa.Text(), nullable=False),
        sa.Column("avatar", sa.String(length=500), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("github_url", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=120), nullable=False),
        sa.Column("icp_filing", sa.String(length=120), nullable=False),
        sa.Column("icp_link", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("site_configs")
    op.drop_index(op.f("ix_post_revisions_post_id"), table_name="post_revisions")
    op.drop_index(op.f("ix_post_revisions_id"), table_name="post_revisions")
    op.drop_table("post_revisions")
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_table("images")
    op.drop_index(op.f("ix_friend_links_id"), table_name="friend_links")
    op.drop_table("friend_links")
    op.drop_index(op.f("ix_messages_parent_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_comments_parent_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_table("post_tags")
    op.drop_index(op.f("ix_posts_status"), table_name="posts")
    op.drop_index(op.f("ix_posts_category_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_published_at"), table_name="posts")
    op.drop_index(op.f("ix_posts_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
