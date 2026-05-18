"""Helper utilities"""

import time
import uuid
from typing import Dict, Any


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID with prefix"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_chat_response(content: str, model: str) -> Dict[str, Any]:
    """Create a chat completion response"""
    return {
        "id": generate_id("chatcmpl"),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }


def create_chunk_response(content: str, model: str, chat_id: str, finish_reason: str = None) -> Dict[str, Any]:
    """Create a streaming chunk response"""
    return {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {"content": content} if content else {},
            "finish_reason": finish_reason
        }]
    }