import json

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.deps import CurrentUser
from app.core.config import settings
from app.schemas.chat import ChatRequest, ModelInfo

router = APIRouter(prefix="/ai", tags=["ai"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/models", response_model=list[ModelInfo])
async def list_models(_user: CurrentUser):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{settings.LLM_BASE_URL}/v1/models")
        resp.raise_for_status()
    data = resp.json()
    return [
        ModelInfo(
            name=m.get("id", ""),
            size=m.get("size"),
            modified_at=m.get("modified_at", ""),
        )
        for m in data.get("data", [])
    ]


@router.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, req: ChatRequest, _user: CurrentUser):
    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=float(settings.LLM_TIMEOUT), write=10, pool=10)) as client:
                async with client.stream(
                    "POST",
                    f"{settings.LLM_BASE_URL}/v1/chat/completions",
                    json={
                        "model": req.model,
                        "messages": [m.model_dump() for m in req.messages],
                        "stream": True,
                    },
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        payload = line[6:]
                        if payload.strip() == "[DONE]":
                            yield "data: [DONE]\n\n"
                            break
                        chunk = json.loads(payload)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
        except httpx.ConnectError:
            yield f"data: {json.dumps({'error': 'Cannot connect to AI server. Please ensure llama-server is running.'})}\n\n"
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'AI server request timed out. Please try again.'})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'error': 'An unexpected error occurred during AI response.'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
