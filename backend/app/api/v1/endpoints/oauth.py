"""GitHub OAuth endpoints."""

import secrets

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.v1.deps import DBSession
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User
from app.schemas.user import Token

router = APIRouter(prefix="/auth/github", tags=["auth"])


@router.get("")
def github_login():
    """Redirect to GitHub OAuth consent page."""
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&scope=user:email"
    )
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/callback", response_model=Token)
async def github_callback(code: str, db: DBSession):
    """Handle GitHub OAuth callback — exchange code for token, create/login user."""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

    # Exchange code for access token
    async with httpx.AsyncClient(timeout=10.0) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        github_token = token_data.get("access_token")
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub OAuth failed")

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        github_user = user_resp.json()

        # Get email (may be private)
        emails_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        emails = emails_resp.json()
        primary_email = next(
            (e["email"] for e in emails if e.get("primary")),
            github_user.get("email"),
        )

    github_id = str(github_user.get("id"))
    username = f"gh_{github_user.get('login', github_id)}"
    avatar = github_user.get("avatar_url", "")

    # Find or create user
    user = db.scalar(select(User).where(User.email == primary_email))
    if not user:
        user = User(
            username=username,
            email=primary_email,
            password_hash=hash_password(secrets.token_hex(32)),
            avatar=avatar,
            email_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate tokens
    access = create_access_token(data={"sub": str(user.id)})
    refresh = create_refresh_token(data={"sub": str(user.id)})
    user.refresh_token = refresh
    db.commit()

    return Token(access_token=access, refresh_token=refresh)
