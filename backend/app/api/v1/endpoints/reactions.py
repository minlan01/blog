from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError

from app.api.v1.deps import DBSession, CurrentUser
from app.models.post import Post
from app.models.post_reaction import PostReaction

router = APIRouter(prefix="/posts", tags=["reactions"])
limiter = Limiter(key_func=get_remote_address)

REACTION_TYPES = {"like", "bookmark"}


@router.post("/{post_id}/reactions")
@limiter.limit("30/minute")
def toggle_reaction(
    request: Request,
    post_id: int,
    body: dict,
    db: DBSession,
    user: CurrentUser,
):
    """Toggle a reaction (like/bookmark) on a post.

    Idempotent: if the reaction already exists, it's removed (toggle behavior).
    If it doesn't exist, it's added.
    """
    reaction_type = body.get("type")
    if reaction_type not in REACTION_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid reaction type. Must be one of {REACTION_TYPES}")

    # Check post exists
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check existing reaction
    existing = db.scalar(
        select(PostReaction).where(
            PostReaction.post_id == post_id,
            PostReaction.user_id == user.id,
            PostReaction.type == reaction_type,
        )
    )

    if existing:
        # Toggle off
        db.delete(existing)
        db.commit()
        action = "removed"
    else:
        # Toggle on
        reaction = PostReaction(
            post_id=post_id,
            user_id=user.id,
            type=reaction_type,
        )
        db.add(reaction)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # Race condition: another request already created it
            action = "exists"
        else:
            action = "added"

    # Count total reactions of this type
    count = db.scalar(
        select(func.count()).select_from(PostReaction).where(
            PostReaction.post_id == post_id,
            PostReaction.type == reaction_type,
        )
    ) or 0

    return {"action": action, "type": reaction_type, "count": count}


@router.get("/{post_id}/reactions")
def get_reactions(post_id: int, db: DBSession):
    """Get reaction counts for a post."""
    if not db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.scalar(
        select(func.count()).select_from(PostReaction).where(
            PostReaction.post_id == post_id,
            PostReaction.type == "like",
        )
    ) or 0

    bookmarks = db.scalar(
        select(func.count()).select_from(PostReaction).where(
            PostReaction.post_id == post_id,
            PostReaction.type == "bookmark",
        )
    ) or 0

    return {"likes": likes, "bookmarks": bookmarks}


@router.get("/me/bookmarks")
def my_bookmarks(db: DBSession, user: CurrentUser):
    """Get current user's bookmarked posts."""
    reactions = db.scalars(
        select(PostReaction).where(
            PostReaction.user_id == user.id,
            PostReaction.type == "bookmark",
        ).order_by(PostReaction.created_at.desc())
    ).all()

    post_ids = [r.post_id for r in reactions]
    posts = []
    if post_ids:
        post_list = db.scalars(
            select(Post).where(Post.id.in_(post_ids)).order_by(Post.published_at.desc())
        ).all()
        posts = post_list

    return {"items": posts, "total": len(posts)}
