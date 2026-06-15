from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., max_length=10000)


class ChatRequest(BaseModel):
    model: str = Field(..., max_length=100)
    messages: list[ChatMessage] = Field(..., max_length=50)


class ModelInfo(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None
