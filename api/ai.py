from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import json
import asyncio

from services.claude_service import claude_service
from services.config import config

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "claude-sonnet-4-20250514"
    messages: List[Message]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ModelResponse(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "anthropic"


def get_account_from_auth(authorization: Optional[str] = None) -> dict:
    """Get account from authorization header or return default"""
    if authorization:
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        for acc in config.accounts:
            if acc.get("session_key") == token or acc.get("account_id") == token:
                return acc
    # Get active accounts
    active_accounts = [acc for acc in config.accounts if acc.get("active", True)]
    if active_accounts:
        return active_accounts[0]
    raise HTTPException(status_code=401, detail="No account available. Please add a session_key in config.json or via /v1/accounts endpoint")


@router.get("/models")
async def list_models():
    """List available models"""
    models = [
        {"id": "claude-sonnet-4-20250514", "object": "model", "created": 1715000000, "owned_by": "anthropic"},
        {"id": "claude-opus-4-20250514", "object": "model", "created": 1715000000, "owned_by": "anthropic"},
        {"id": "claude-3-5-sonnet-20241022", "object": "model", "created": 1700000000, "owned_by": "anthropic"},
        {"id": "claude-3-5-haiku-20241022", "object": "model", "created": 1700000000, "owned_by": "anthropic"},
    ]
    return {"object": "list", "data": models}


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """OpenAI-compatible chat completions endpoint"""
    account = get_account_from_auth(authorization)

    if request.stream:
        return StreamingResponse(
            stream_chat_response(request, account),
            media_type="text/event-stream"
        )
    else:
        response = await claude_service.chat(
            account=account,
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response


async def stream_chat_response(request: ChatCompletionRequest, account: dict):
    """Stream chat response in OpenAI format"""
    import time
    chat_id = f"chatcmpl-{int(time.time())}"

    async for chunk in claude_service.chat_stream(
        account=account,
        model=request.model,
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    ):
        data = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "delta": {"content": chunk} if chunk else {"finish_reason": "stop"},
                "finish_reason": None if chunk else "stop"
            }]
        }
        yield f"data: {json.dumps(data)}\n\n"

    yield "data: [DONE]\n\n"