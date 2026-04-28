from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.v1.deps import DBSession
from app.models.comment import Comment
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.models.message import Message
from app.models.friend_link import FriendLink

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(db: DBSession):
    post_count = db.scalar(select(func.count()).select_from(Post)) or 0
    category_count = db.scalar(select(func.count()).select_from(Category)) or 0
    tag_count = db.scalar(select(func.count()).select_from(Tag)) or 0
    comment_count = db.scalar(select(func.count()).select_from(Comment)) or 0
    user_count = db.scalar(select(func.count()).select_from(User)) or 0
    message_count = db.scalar(select(func.count()).select_from(Message)) or 0
    friend_link_count = db.scalar(select(func.count()).select_from(FriendLink)) or 0
    total_views = db.scalar(select(func.coalesce(func.sum(Post.view_count), 0))) or 0
    total_words = db.scalar(
        select(func.coalesce(func.sum(func.length(Post.content_markdown)), 0))
    ) or 0

    return {
        "posts": post_count,
        "categories": category_count,
        "tags": tag_count,
        "comments": comment_count,
        "users": user_count,
        "messages": message_count,
        "friend_links": friend_link_count,
        "total_views": total_views,
        "total_words": total_words,
    }
