"""Personal Access Token (PAT) 管理端点"""
import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.v1.deps import DBSession, SuperAdmin
from app.models.access_token import AccessToken

router = APIRouter(prefix="/tokens", tags=["tokens"])


class TokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="令牌用途，如 'AI发文章'")
    scopes: str = Field(default="*", max_length=200, description="权限范围，如 posts:create,upload")
    expires_in_days: int | None = Field(default=None, ge=1, le=365, description="过期天数，不填=永不过期")


class TokenRead(BaseModel):
    id: int
    name: str
    scopes: str
    expires_at: datetime | None
    last_used_at: datetime | None
    created_at: datetime
    revoked: bool

    model_config = {"from_attributes": True}


class TokenCreateResponse(BaseModel):
    """创建成功后返回——明文令牌只显示这一次"""
    token: str
    token_info: TokenRead


@router.get("", response_model=list[TokenRead])
def list_tokens(admin: SuperAdmin, db: DBSession):
    """列出当前管理员的所有令牌"""
    tokens = list(db.scalars(
        select(AccessToken)
        .where(AccessToken.user_id == admin.id)
        .order_by(AccessToken.created_at.desc())
    ).all())
    return tokens


@router.post("", response_model=TokenCreateResponse, status_code=201)
def create_token(body: TokenCreate, admin: SuperAdmin, db: DBSession):
    """创建新令牌。明文令牌只在此响应中返回一次。"""
    # 生成令牌：pat_ + 40 字符随机串
    raw_token = "pat_" + secrets.token_hex(20)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    expires_at = None
    if body.expires_in_days:
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

    token = AccessToken(
        user_id=admin.id,
        name=body.name,
        token_hash=token_hash,
        scopes=body.scopes,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    return TokenCreateResponse(
        token=raw_token,
        token_info=TokenRead.model_validate(token),
    )


@router.delete("/{token_id}", status_code=204)
def revoke_token(token_id: int, admin: SuperAdmin, db: DBSession):
    """撤销令牌（立即失效）"""
    token = db.get(AccessToken, token_id)
    if not token or token.user_id != admin.id:
        raise HTTPException(status_code=404, detail="令牌不存在")
    token.revoked = True
    db.commit()
