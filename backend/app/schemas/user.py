from datetime import datetime

from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, pattern=r'^[a-zA-Z0-9]+$')
    password: str = Field(..., min_length=8, max_length=100)
    email: str | None = None

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('Username can only contain English letters (a-z, A-Z) and numbers (0-9)')
        return v


class UserRead(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str
    bio: str | None = None
    avatar: str | None = None
    email_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    bio: str | None = None
    avatar: str | None = None
    email: str | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = None
    bio: str | None = None
    avatar: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str
