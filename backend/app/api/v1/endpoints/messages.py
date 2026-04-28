import random

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, CurrentUser
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])
limiter = Limiter(key_func=get_remote_address)

COLORS = ["#818cf8", "#f59e0b", "#10b981", "#ef4444", "#ec4899", "#06b6d4"]


def _message_to_read(m: Message, include_replies: bool = False) -> MessageRead:
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
    mr = MessageRead.model_validate(data)
    if include_replies and m.replies:
        mr.replies = [_message_to_read(r, include_replies=True) for r in m.replies if r.id != m.id]
    return mr


@router.get("", response_model=list[MessageRead])
def list_messages(db: DBSession):
    stmt = (
        select(Message)
        .options(joinedload(Message.replies))
        .where(Message.parent_id.is_(None))
        .order_by(Message.created_at.desc())
    )
    messages = list(db.scalars(stmt).unique().all())
    return [_message_to_read(m, include_replies=True) for m in messages]


@router.post("", response_model=MessageRead, status_code=201)
@limiter.limit("10/minute")
def create_message(request: Request, body: MessageCreate, db: DBSession):
    if body.parent_id:
        parent = db.get(Message, body.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父留言不存在")

    msg = Message(
        name=body.name,
        email=body.email,
        content=body.content,
        color=random.choice(COLORS),
        parent_id=body.parent_id,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _message_to_read(msg, include_replies=False)


@router.delete("/{message_id}", status_code=204)
def delete_message(message_id: int, db: DBSession, user: CurrentUser):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="留言不存在")
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除留言")
    db.delete(msg)
    db.commit()
