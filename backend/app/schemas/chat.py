from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., max_length=10000)


class ChatRequest(BaseModel):
    model: str = Field(..., max_length=100)
    messages: list[ChatMessage] = Field(..., max_length=50)
    session_id: int | None = Field(default=None, description="关联会话 ID，传入则自动保存")


class ModelInfo(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None


# ── 会话管理 Schema ──


class ChatSessionCreate(BaseModel):
    title: str = Field(default="新对话", max_length=200)
    model: str | None = Field(default=None, max_length=100)


class ChatSessionSummary(BaseModel):
    """会话列表项（不含消息内容）"""

    id: int
    title: str
    model: str | None = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetail(BaseModel):
    """会话详情（含所有消息）"""

    id: int
    title: str
    model: str | None = None
    messages: list[ChatMessageOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


# ── 记忆 Schema ──


class ChatMemory(BaseModel):
    """AI 记忆（跨会话 system prompt）"""

    memory: str = Field(default="", max_length=5000)


# ── 流式响应中保存用户消息 ──


class ChatWithSaveRequest(BaseModel):
    model: str = Field(..., max_length=100)
    messages: list[ChatMessage] = Field(..., max_length=50)
    session_id: int | None = Field(default=None)
    user_message: str | None = Field(default=None, max_length=10000, description="要保存的用户消息原文")
