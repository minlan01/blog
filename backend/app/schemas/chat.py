from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]


class ModelInfo(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None
