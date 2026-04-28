from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

DBSession = Annotated[Session, Depends(get_db)]


def _extract_token(request: Request) -> str | None:
    """Extract Bearer token from Authorization header or fallback to query param."""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    # Fallback for backward compat: query param
    return request.query_params.get("token")


def get_current_user(request: Request, db: DBSession) -> User:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token provided")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_super_admin(request: Request, db: DBSession) -> User:
    user = get_current_user(request, db)
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
SuperAdmin = Annotated[User, Depends(require_super_admin)]
