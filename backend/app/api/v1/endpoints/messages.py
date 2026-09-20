import random
import logging

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, CurrentUser
from app.core.config import settings
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageRead, PublicMessageRead, message_to_read, public_message_to_read
from app.utils.tree import collect_descendant_ids

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/messages", tags=["messages"])
limiter = Limiter(key_func=get_remote_address)

COLORS = ["#818cf8", "#f59e0b", "#10b981", "#ef4444", "#ec4899", "#06b6d4"]


def _get_message_children(db, message_id: int) -> list[tuple[int]]:
    children = list(db.scalars(select(Message).where(Message.parent_id == message_id)).all())
    return [(c.id,) for c in children]


def _notify_admin_new_message(msg: Message) -> None:
    """Send email notification to admin about a new message."""
    try:
        from app.core.email import _send_email
        from app.models.site_config import SiteConfig
        from app.db.session import SessionLocal

        db = SessionLocal()
        site = db.scalar(select(SiteConfig).limit(1))
        db.close()

        if not site or not site.email:
            return

        subject = f"[博客留言] {msg.name} 给你留言了"
        body = f"""新留言通知

留言人：{msg.name}
邮箱：{msg.email or '未提供'}
内容：{msg.content}
时间：{msg.created_at.strftime('%Y-%m-%d %H:%M') if msg.created_at else 'N/A'}

请登录后台审核：https://chiyeblog.cn/admin
"""
        _send_email(site.email, subject, body)
        logger.info("New message notification sent to %s", site.email)
    except Exception as e:
        logger.warning("Failed to send message notification: %s", e)


@router.get("", response_model=list[PublicMessageRead])
def list_messages(db: DBSession):
    """Public list — only approved messages"""
    stmt = (
        select(Message)
        .options(joinedload(Message.replies))
        .where(Message.parent_id.is_(None), Message.status == "approved")
        .order_by(Message.created_at.desc())
    )
    messages = list(db.scalars(stmt).unique().all())
    result = []
    for m in messages:
        read = public_message_to_read(m, include_replies=True)
        if read.replies:
            read.replies = [r for r in read.replies if getattr(r, "status", "approved") == "approved"]
        result.append(read)
    return result


class MessageCreateSimple(MessageCreate):
    """Captcha fields optional — no longer required"""
    captcha_token: str | None = None
    captcha_ts: int | None = None


@router.post("", response_model=PublicMessageRead, status_code=201)
@limiter.limit("10/minute")
def create_message(request: Request, body: MessageCreateSimple, db: DBSession):
    if body.parent_id:
        parent = db.get(Message, body.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父留言不存在")

    is_reply = body.parent_id is not None

    msg = Message(
        name=body.name,
        email=body.email,
        content=body.content,
        color=random.choice(COLORS),
        parent_id=body.parent_id,
        # 统一审核：顶级留言和回复都需 pending
        status="pending",
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    _notify_admin_new_message(msg)

    return public_message_to_read(msg, include_replies=False)


@router.delete("/{message_id}", status_code=204)
def delete_message(message_id: int, db: DBSession, user: CurrentUser):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="留言不存在")
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除留言")
    descendant_ids = collect_descendant_ids(message_id, lambda mid: _get_message_children(db, mid))
    for mid in reversed(descendant_ids):
        m = db.get(Message, mid)
        if m:
            db.delete(m)
    db.delete(msg)
    db.commit()
