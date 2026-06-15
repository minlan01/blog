from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, CurrentUser
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentRead, comment_to_read

router = APIRouter(prefix="/comments", tags=["comments"])
limiter = Limiter(key_func=get_remote_address)


def _collect_comment_descendant_ids(db, comment_id: int) -> list[int]:
    ids: list[int] = []
    children = list(db.scalars(select(Comment).where(Comment.parent_id == comment_id)).all())
    for child in children:
        ids.append(child.id)
        ids.extend(_collect_comment_descendant_ids(db, child.id))
    return ids


@router.get("", response_model=list[CommentRead])
def list_comments(post_id: int, db: DBSession):
    stmt = (
        select(Comment)
        .options(joinedload(Comment.author), joinedload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
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
    descendant_ids = _collect_comment_descendant_ids(db, comment_id)
    for cid in reversed(descendant_ids):
        c = db.get(Comment, cid)
        if c:
            db.delete(c)
    db.delete(comment)
    db.commit()
