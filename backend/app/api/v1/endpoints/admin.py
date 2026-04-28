"""
管理后台接口 — 需要 super_admin 权限
"""
import io
import re
import zipfile
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, SuperAdmin
from app.models.comment import Comment
from app.models.message import Message
from app.models.post import Post, post_tags
from app.models.post_revision import PostRevision
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.comment import CommentRead
from app.schemas.message import AdminReplyCreate, MessageRead
from app.schemas.post import PostCreate, PostDetail, PostUpdate
from app.schemas.site import SiteProfile, SiteProfileUpdate
from app.schemas.tag import TagCreate, TagRead, TagUpdate
from app.schemas.user import UserRead
from app.schemas.user import AdminUserUpdate
from app.services.blog_service import BlogService

router = APIRouter(prefix="/admin", tags=["admin"])


# ────────────── Posts ──────────────

@router.get("/posts", response_model=list[PostDetail])
def list_posts(db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    return service.list_all_posts()


@router.post("/posts", response_model=PostDetail, status_code=201)
def create_post(body: PostCreate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    if service.get_post_by_slug(body.slug, published_only=False):
        raise HTTPException(status_code=409, detail=f"slug '{body.slug}' already exists")
    data = body.model_dump(exclude={"tag_ids"})
    return service.create_post(data, body.tag_ids)


@router.put("/posts/{post_id}", response_model=PostDetail)
def update_post(post_id: int, body: PostUpdate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    if body.slug:
        existing = service.get_post_by_slug(body.slug, published_only=False)
        if existing and existing.id != post_id:
            raise HTTPException(status_code=409, detail=f"slug '{body.slug}' is used by another post")
    data = body.model_dump(exclude={"tag_ids"}, exclude_unset=True)
    post = service.update_post(post_id, data, body.tag_ids)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    if not service.delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")


# ────────────── Categories ──────────────

@router.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(body: CategoryCreate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    return service.create_category(body.model_dump())


@router.put("/categories/{cat_id}", response_model=CategoryRead)
def update_category(cat_id: int, body: CategoryUpdate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    cat = service.update_category(cat_id, body.model_dump(exclude_unset=True))
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    if not service.delete_category(cat_id):
        raise HTTPException(status_code=404, detail="Category not found")


# ────────────── Tags ──────────────

@router.post("/tags", response_model=TagRead, status_code=201)
def create_tag(body: TagCreate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    return service.create_tag(body.model_dump())


@router.put("/tags/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, body: TagUpdate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    tag = service.update_tag(tag_id, body.model_dump(exclude_unset=True))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    if not service.delete_tag(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")


# ────────────── Site Profile ──────────────

@router.put("/site/profile", response_model=SiteProfile)
def update_site_profile(body: SiteProfileUpdate, db: DBSession, _admin: SuperAdmin):
    service = BlogService(db)
    profile = service.update_site_profile(body.model_dump(exclude_unset=True))
    if not profile:
        raise HTTPException(status_code=404, detail="Site config not found")
    return profile


# ────────────── User Management ──────────────

@router.get("/users", response_model=list[UserRead])
def list_users(db: DBSession, _admin: SuperAdmin):
    stmt = select(User).order_by(User.created_at.desc())
    return list(db.scalars(stmt).all())


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, body: AdminUserUpdate, db: DBSession, _admin: SuperAdmin):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: DBSession, admin: SuperAdmin):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()


# ────────────── Comment Management ──────────────

def _comment_to_read(c: Comment) -> CommentRead:
    data = {
        "id": c.id,
        "content": c.content,
        "post_id": c.post_id,
        "user_id": c.user_id,
        "parent_id": c.parent_id,
        "is_approved": c.is_approved,
        "created_at": c.created_at,
        "author_name": c.author.username if c.author else None,
        "replies": [],
    }
    cr = CommentRead.model_validate(data)
    if c.replies:
        cr.replies = [_comment_to_read(r) for r in c.replies if r.id != c.id]
    return cr


@router.get("/comments", response_model=list[CommentRead])
def list_all_comments(db: DBSession, _admin: SuperAdmin, post_id: int | None = None):
    stmt = select(Comment).options(joinedload(Comment.author), joinedload(Comment.replies)).order_by(Comment.created_at.desc())
    if post_id:
        stmt = stmt.where(Comment.post_id == post_id)
    comments = list(db.scalars(stmt).unique().all())
    return [_comment_to_read(c) for c in comments]


@router.put("/comments/{comment_id}/approve", response_model=CommentRead)
def approve_comment(comment_id: int, db: DBSession, _admin: SuperAdmin):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    comment.is_approved = True
    db.commit()
    db.refresh(comment)
    return _comment_to_read(comment)


@router.delete("/comments/{comment_id}", status_code=204)
def admin_delete_comment(comment_id: int, db: DBSession, _admin: SuperAdmin):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    db.delete(comment)
    db.commit()


# ────────────── Message Management ──────────────

def _admin_msg_to_read(m: Message) -> MessageRead:
    data = {
        "id": m.id,
        "name": m.name,
        "email": m.email,
        "content": m.content,
        "color": m.color,
        "parent_id": m.parent_id,
        "admin_reply": m.admin_reply,
        "admin_reply_at": m.admin_reply_at,
        "created_at": m.created_at,
        "replies": [],
    }
    return MessageRead.model_validate(data)


@router.get("/messages", response_model=list[MessageRead])
def list_all_messages(db: DBSession, _admin: SuperAdmin):
    stmt = select(Message).order_by(Message.created_at.desc())
    messages = list(db.scalars(stmt).all())
    return [_admin_msg_to_read(m) for m in messages]


@router.put("/messages/{message_id}/reply", response_model=MessageRead)
def reply_message(message_id: int, body: AdminReplyCreate, db: DBSession, _admin: SuperAdmin):
    from datetime import datetime, timezone
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="留言不存在")
    msg.admin_reply = body.content
    msg.admin_reply_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)
    return msg


@router.delete("/messages/{message_id}", status_code=204)
def admin_delete_message(message_id: int, db: DBSession, _admin: SuperAdmin):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="留言不存在")
    db.delete(msg)
    db.commit()


# ────────────── Post Revisions ──────────────

@router.get("/posts/{post_id}/revisions")
def list_post_revisions(post_id: int, db: DBSession, _admin: SuperAdmin):
    revisions = list(
        db.scalars(
            select(PostRevision)
            .where(PostRevision.post_id == post_id)
            .order_by(PostRevision.version_number.desc())
        ).all()
    )
    return [
        {
            "id": r.id,
            "post_id": r.post_id,
            "title": r.title,
            "summary": r.summary,
            "version_number": r.version_number,
            "created_at": r.created_at,
        }
        for r in revisions
    ]


@router.get("/posts/{post_id}/revisions/{rev_id}")
def get_post_revision(post_id: int, rev_id: int, db: DBSession, _admin: SuperAdmin):
    rev = db.get(PostRevision, rev_id)
    if not rev or rev.post_id != post_id:
        raise HTTPException(status_code=404, detail="Revision not found")
    return {
        "id": rev.id,
        "post_id": rev.post_id,
        "title": rev.title,
        "content_markdown": rev.content_markdown,
        "summary": rev.summary,
        "version_number": rev.version_number,
        "created_at": rev.created_at,
    }


@router.post("/posts/{post_id}/revisions/{rev_id}/restore", response_model=PostDetail)
def restore_post_revision(post_id: int, rev_id: int, db: DBSession, _admin: SuperAdmin):
    rev = db.get(PostRevision, rev_id)
    if not rev or rev.post_id != post_id:
        raise HTTPException(status_code=404, detail="Revision not found")

    service = BlogService(db)
    post = service.update_post(post_id, {
        "title": rev.title,
        "content_markdown": rev.content_markdown,
        "summary": rev.summary or "",
    })
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# ────────────── Batch Operations ──────────────

@router.post("/posts/batch-delete", status_code=204)
def batch_delete_posts(body: dict, db: DBSession, _admin: SuperAdmin):
    ids = body.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")
    service = BlogService(db)
    for post_id in ids:
        service.delete_post(post_id)


@router.post("/comments/batch-action")
def batch_action_comments(body: dict, db: DBSession, _admin: SuperAdmin):
    ids = body.get("ids", [])
    action = body.get("action")  # "approve" or "delete"
    if not ids or not action:
        raise HTTPException(status_code=400, detail="ids and action required")

    for comment_id in ids:
        comment = db.get(Comment, comment_id)
        if not comment:
            continue
        if action == "approve":
            comment.is_approved = True
        elif action == "delete":
            db.delete(comment)
    db.commit()
    return {"message": f"Batch {action} completed", "count": len(ids)}


# ────────────── Export/Import ──────────────

@router.get("/posts/export")
def export_posts(db: DBSession, _admin: SuperAdmin):
    """Export all posts as a zip of Markdown files."""
    posts = list(
        db.scalars(
            select(Post).options(joinedload(Post.category), joinedload(Post.tags))
        ).unique().all()
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for post in posts:
            frontmatter = f"""---
title: "{post.title}"
slug: "{post.slug}"
summary: "{post.summary}"
status: "{post.status}"
published_at: "{post.published_at.isoformat() if post.published_at else ''}"
category: "{post.category.name if post.category else ''}"
tags: [{', '.join(f'"{t.name}"' for t in post.tags)}]
is_featured: {post.is_featured}
---

"""
            content = frontmatter + post.content_markdown
            filename = re.sub(r'[^\w\s-]', '', post.slug) + '.md'
            zf.writestr(filename, content)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=blog_posts.zip"},
    )


@router.post("/posts/import")
async def import_posts(_admin: SuperAdmin, db: DBSession, file: UploadFile = File(...)):
    """Import posts from a zip of Markdown files with YAML frontmatter."""
    content = await file.read()
    imported = []
    service = BlogService(db)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for name in zf.namelist():
            if not name.endswith('.md'):
                continue
            md_content = zf.read(name).decode('utf-8')

            # Parse simple frontmatter
            data = {
                "title": "",
                "slug": name.replace('.md', ''),
                "summary": "",
                "content_markdown": "",
                "status": "published",
            }
            body_start = 0
            if md_content.startswith('---'):
                end = md_content.find('---', 3)
                if end != -1:
                    frontmatter = md_content[3:end].strip()
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, _, val = line.partition(':')
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key == 'title':
                                data['title'] = val
                            elif key == 'slug':
                                data['slug'] = val
                            elif key == 'summary':
                                data['summary'] = val
                            elif key == 'status':
                                data['status'] = val
                    body_start = end + 3

            data['content_markdown'] = md_content[body_start:].strip()
            if not data['title']:
                data['title'] = data['slug'].replace('-', ' ').title()

            # Skip if slug exists
            if service.get_post_by_slug(data['slug'], published_only=False):
                continue

            post = service.create_post(data, [])
            imported.append({"id": post.id, "title": post.title})

    return {"imported": imported, "count": len(imported)}


# ────────────── Comment Moderation ──────────────

@router.get("/comments/pending", response_model=list[CommentRead])
def list_pending_comments(db: DBSession, _admin: SuperAdmin):
    """List unapproved comments for moderation."""
    stmt = (
        select(Comment)
        .options(joinedload(Comment.author), joinedload(Comment.replies))
        .where(Comment.is_approved == False)
        .order_by(Comment.created_at.desc())
    )
    comments = list(db.scalars(stmt).unique().all())
    return [_comment_to_read(c) for c in comments]


@router.put("/comments/{comment_id}/reject")
def reject_comment(comment_id: int, db: DBSession, _admin: SuperAdmin):
    """Reject (delete) a comment."""
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    db.delete(comment)
    db.commit()
    return {"message": "Comment rejected"}
