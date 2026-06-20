import json

import httpx
from fastapi import APIRouter, HTTPException, Request
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
    if not settings.llm_api_key:
        return [
            ModelInfo(
                name=settings.LLM_DEFAULT_MODEL,
                size=None,
                modified_at=None,
            )
        ]

    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{settings.llm_base_url}/models", headers=headers)
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
    if not settings.llm_api_key:
        raise HTTPException(status_code=503, detail="DeepSeek API key is not configured.")

    async def event_stream():
        try:
            headers = {
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=float(settings.LLM_TIMEOUT), write=10, pool=10)) as client:
                async with client.stream(
                    "POST",
                    f"{settings.llm_base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": req.model or settings.LLM_DEFAULT_MODEL,
                        "messages": [m.model_dump() for m in req.messages],
                        "stream": True,
                    },
                ) as resp:
                    if resp.status_code >= 400:
                        body = await resp.aread()
                        message = "DeepSeek API request failed."
                        try:
                            message = json.loads(body.decode("utf-8")).get("error", {}).get("message", message)
                        except Exception:
                            text = body.decode("utf-8", errors="ignore").strip()
                            if text:
                                message = text
                        yield f"data: {json.dumps({'error': message})}\n\n"
                        return
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
        except httpx.HTTPStatusError:
            yield f"data: {json.dumps({'error': 'DeepSeek API request failed.'})}\n\n"
        except httpx.ConnectError:
            yield f"data: {json.dumps({'error': 'Cannot connect to DeepSeek API. Please check the network and API base URL.'})}\n\n"
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'DeepSeek API request timed out. Please try again.'})}\n\n"
        except Exception:
            yield f"data: {json.dumps({'error': 'An unexpected error occurred during AI response.'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
