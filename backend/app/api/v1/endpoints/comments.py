from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, CurrentUser
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentRead, comment_to_read
from app.utils.tree import collect_descendant_ids

router = APIRouter(prefix="/comments", tags=["comments"])
limiter = Limiter(key_func=get_remote_address)


def _get_comment_children(db, comment_id: int) -> list[tuple[int]]:
    children = list(db.scalars(select(Comment).where(Comment.parent_id == comment_id)).all())
    return [(c.id,) for c in children]


@router.get("", response_model=list[CommentRead])
def list_comments(post_id: int, db: DBSession):
    stmt = (
        select(Comment)
        .options(joinedload(Comment.author), joinedload(Comment.replies))
        .where(
            Comment.post_id == post_id,
            Comment.parent_id.is_(None),
            Comment.is_approved == True,  # 公共接口只返回已审核评论
        )
        .order_by(Comment.created_at.asc())
    )
    comments = list(db.scalars(stmt).unique().all())
    return [comment_to_read(c, include_replies=True) for c in comments]


@router.post("", response_model=CommentRead, status_code=201)
@limiter.limit("10/minute")
def create_comment(request: Request, body: CommentCreate, db: DBSession, user: CurrentUser):
    post = db.get(Post, body.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    if body.parent_id:
        parent = db.get(Comment, body.parent_id)
        if not parent or parent.post_id != body.post_id:
            raise HTTPException(status_code=400, detail="父评论不存在或不属于该文章")
        depth = 1
        current = parent
        while current.parent_id:
            depth += 1
            if depth >= 3:
                raise HTTPException(status_code=400, detail="评论嵌套深度不能超过3层")
            current = db.get(Comment, current.parent_id)
            if not current:
                break

    comment = Comment(
        content=body.content,
        post_id=body.post_id,
        user_id=user.id,
        parent_id=body.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment_to_read(comment, include_replies=False)


@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: DBSession, user: CurrentUser):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != user.id and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="无权删除此评论")
    descendant_ids = collect_descendant_ids(comment_id, lambda cid: _get_comment_children(db, cid))
    for cid in reversed(descendant_ids):
        c = db.get(Comment, cid)
        if c:
            db.delete(c)
    db.delete(comment)
    db.commit()


# ── Emoji Reactions ──

ALLOWED_EMOJIS = {"👍", "❤️", "😂", "🎉", "🚀", "👀"}


@router.post("/{comment_id}/reactions")
def toggle_comment_reaction(
    comment_id: int,
    body: dict,
    db: DBSession,
    user: CurrentUser,
):
    """Toggle an emoji reaction on a comment. Idempotent."""
    from app.models.comment_reaction import CommentReaction

    emoji = body.get("emoji", "").strip()
    if emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status_code=422, detail=f"Invalid emoji. Allowed: {ALLOWED_EMOJIS}")

    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    existing = db.scalar(
        select(CommentReaction).where(
            CommentReaction.comment_id == comment_id,
            CommentReaction.user_id == user.id,
            CommentReaction.emoji == emoji,
        )
    )

    if existing:
        db.delete(existing)
        db.commit()
        action = "removed"
    else:
        reaction = CommentReaction(
            comment_id=comment_id,
            user_id=user.id,
            emoji=emoji,
        )
        db.add(reaction)
        try:
            db.commit()
        except Exception:
            db.rollback()
            action = "exists"
        else:
            action = "added"

    # Get counts for this emoji on this comment
    from sqlalchemy import func as _func
    count = db.scalar(
        select(_func.count()).select_from(CommentReaction).where(
            CommentReaction.comment_id == comment_id,
            CommentReaction.emoji == emoji,
        )
    ) or 0

    return {"action": action, "emoji": emoji, "count": count}


@router.get("/{comment_id}/reactions")
def get_comment_reactions(comment_id: int, db: DBSession):
    """Get all emoji reactions for a comment."""
    from app.models.comment_reaction import CommentReaction
    from sqlalchemy import func as _func

    if not db.get(Comment, comment_id):
        raise HTTPException(status_code=404, detail="评论不存在")

    rows = db.execute(
        select(
            CommentReaction.emoji,
            _func.count().label("count"),
        ).where(CommentReaction.comment_id == comment_id)
        .group_by(CommentReaction.emoji)
    ).all()

    return {"reactions": [{"emoji": r[0], "count": r[1]} for r in rows]}
