from app.models.access_token import AccessToken
from app.models.category import Category
from app.models.chat_session import ChatSession, ChatMessageRecord
from app.models.comment import Comment
from app.models.comment_reaction import CommentReaction
from app.models.friend_link import FriendLink
from app.models.image import Image
from app.models.message import Message
from app.models.page_view import PageView
from app.models.post import Post, post_tags
from app.models.post_reaction import PostReaction
from app.models.post_revision import PostRevision
from app.models.site_config import SiteConfig
from app.models.tag import Tag
from app.models.user import User

# Register FTS5 event listeners on the Post model class.
# Done here (not in fts_sync.py top-level) because SQLAlchemy's
# @event.listens_for requires the actual class, not a string name.
# This also avoids circular imports: Post is fully defined by this point.
from app.services.fts_sync import register_fts_events

register_fts_events(Post)

__all__ = [
    "AccessToken",
    "Category",
    "ChatSession",
    "ChatMessageRecord",
    "Comment",
    "CommentReaction",
    "FriendLink",
    "Image",
    "Message",
    "PageView",
    "Post",
    "PostReaction",
    "PostRevision",
    "Tag",
    "SiteConfig",
    "User",
    "post_tags",
]
