import json

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.chat import ChatRequest, ModelInfo

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/models", response_model=list[ModelInfo])
async def list_models():
    async with httpx.AsyncClient() as client:
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
async def chat(req: ChatRequest):
    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
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
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
