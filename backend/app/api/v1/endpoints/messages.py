import random
import hashlib
import time

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.deps import DBSession, CurrentUser
from app.core.config import settings
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageRead, PublicMessageRead, message_to_read, public_message_to_read

router = APIRouter(prefix="/messages", tags=["messages"])
limiter = Limiter(key_func=get_remote_address)

COLORS = ["#818cf8", "#f59e0b", "#10b981", "#ef4444", "#ec4899", "#06b6d4"]


def _collect_message_descendant_ids(db, message_id: int) -> list[int]:
    ids: list[int] = []
    children = list(db.scalars(select(Message).where(Message.parent_id == message_id)).all())
    for child in children:
        ids.append(child.id)
        ids.extend(_collect_message_descendant_ids(db, child.id))
    return ids


def _generate_captcha_token(a: int, b: int, ts: int) -> str:
    raw = f"{a}+{b}:{ts}:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@router.get("/captcha")
def get_captcha(request: Request):
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    ts = int(time.time())
    token = _generate_captcha_token(a, b, ts)
    return {"question": f"{a} + {b} = ?", "token": token, "ts": ts}


def _verify_captcha(answer: int | None, token: str | None, ts: int | None) -> bool:
    if answer is None or token is None or ts is None:
        return False
    now = int(time.time())
    if now - ts > 600:
        return False
    for a in range(1, 21):
        for b in range(1, 21):
            if a + b == answer and _generate_captcha_token(a, b, ts) == token:
                return True
    return False


@router.get("", response_model=list[PublicMessageRead])
def list_messages(db: DBSession):
    stmt = (
        select(Message)
        .options(joinedload(Message.replies))
        .where(Message.parent_id.is_(None))
        .order_by(Message.created_at.desc())
    )
    messages = list(db.scalars(stmt).unique().all())
    return [public_message_to_read(m, include_replies=True) for m in messages]


class MessageCreateWithCaptcha(MessageCreate):
    captcha_token: str | None = None
    captcha_ts: int | None = None


@router.post("", response_model=PublicMessageRead, status_code=201)
@limiter.limit("10/minute")
def create_message(request: Request, body: MessageCreateWithCaptcha, db: DBSession):
    if not _verify_captcha(body.captcha_answer, body.captcha_token, body.captcha_ts):
        raise HTTPException(status_code=400, detail="验证码错误，请重试")
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
    return public_message_to_read(msg, include_replies=False)


@router.delete("/{message_id}", status_code=204)
def delete_message(message_id: int, db: DBSession, user: CurrentUser):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="留言不存在")
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="仅管理员可删除留言")
    descendant_ids = _collect_message_descendant_ids(db, message_id)
    for mid in reversed(descendant_ids):
        m = db.get(Message, mid)
        if m:
            db.delete(m)
    db.delete(msg)
    db.commit()
