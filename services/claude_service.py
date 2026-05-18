"""
Claude Web API Service

This service handles communication with Claude's web interface API.
It uses session keys from browser cookies to authenticate requests.

How to get your session key:
1. Login to claude.ai in your browser
2. Open Developer Tools (F12) -> Application -> Cookies
3. Find the 'sessionKey' cookie value
4. Add it to config.json under accounts with session_key field
"""

import json
import time
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator
import httpx

from .config import config


class ClaudeService:
    BASE_URL = "https://claude.ai"
    API_PREFIX = "/api/organizations"

    def __init__(self):
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._organizations: Dict[str, str] = {}  # account_id -> organization_id
        self._conversations: Dict[str, str] = {}  # session -> conversation_id

    async def init_sessions(self):
        """Initialize HTTP clients for all accounts"""
        for account in config.accounts:
            if account.get("active", True):
                try:
                    await self._init_client(account)
                except Exception as e:
                    print(f"Failed to init client for account {account.get('account_id')}: {e}")

    async def _init_client(self, account: Dict[str, Any]) -> httpx.AsyncClient:
        """Initialize HTTP client for an account"""
        account_id = account.get("account_id", "default")

        if account_id in self._clients:
            return self._clients[account_id]

        session_key = account.get("session_key")
        if not session_key:
            raise ValueError(f"No session_key for account {account_id}")

        proxy = None
        if config.proxy.get("enabled"):
            proxy = config.proxy.get("https") or config.proxy.get("http")

        client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=30.0),
            proxies=proxy if proxy else None,
            headers={
                "Accept": "text/event-stream",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
            cookies={"sessionKey": session_key},
            follow_redirects=True,
        )

        self._clients[account_id] = client

        # Get organization ID
        await self._fetch_organization_id(account_id, client)

        return client

    async def _fetch_organization_id(self, account_id: str, client: httpx.AsyncClient):
        """Fetch organization ID for the account"""
        try:
            response = await client.get(f"{self.BASE_URL}/api/organizations")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    org_id = data[0].get("uuid") or data[0].get("id")
                    if org_id:
                        self._organizations[account_id] = org_id
        except Exception:
            # Use default organization ID pattern
            pass

    async def close_sessions(self):
        """Close all HTTP clients"""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    async def _get_client(self, account: Dict[str, Any]) -> httpx.AsyncClient:
        """Get or create HTTP client for account"""
        account_id = account.get("account_id", "default")

        if account_id not in self._clients:
            return await self._init_client(account)

        return self._clients[account_id]

    async def chat(
        self,
        account: Dict[str, Any],
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a non-streaming chat request"""
        full_content = ""
        async for chunk in self.chat_stream(
            account, model, messages, temperature, max_tokens
        ):
            full_content += chunk

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": full_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }

    async def chat_stream(
        self,
        account: Dict[str, Any],
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Send a streaming chat request"""
        client = await self._get_client(account)
        account_id = account.get("account_id", "default")

        org_id = self._organizations.get(account_id)
        if not org_id:
            # Try to fetch organization ID again
            try:
                await self._fetch_organization_id(account_id, client)
                org_id = self._organizations.get(account_id)
            except Exception:
                pass
            if not org_id:
                raise ValueError(f"No organization ID for account {account_id}. Please check your session key.")

        # Create or get conversation
        conversation_id = await self._create_conversation(client, org_id)

        # Build prompt from messages
        prompt = self._build_prompt(messages)

        # Build request body
        request_body = {
            "prompt": prompt,
            "timezone": "UTC",
            "model": model,
        }

        if temperature is not None:
            request_body["temperature"] = temperature
        if max_tokens is not None:
            request_body["max_tokens"] = max_tokens

        # Send message
        url = f"{self.BASE_URL}{self.API_PREFIX}/{org_id}/chat_conversations/{conversation_id}/completion"

        async with client.stream("POST", url, json=request_body) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"Claude API error: {response.status_code} - {error_text.decode()}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "completion" in data:
                            yield data["completion"]
                    except json.JSONDecodeError:
                        continue

    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build a prompt string from messages"""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"Human: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        parts.append("Assistant:")
        return "\n\n".join(parts)

    async def _create_conversation(self, client: httpx.AsyncClient, org_id: str) -> str:
        """Create a new conversation"""
        url = f"{self.BASE_URL}{self.API_PREFIX}/{org_id}/chat_conversations"
        response = await client.post(url, json={})

        if response.status_code == 200:
            data = response.json()
            return data.get("uuid") or data.get("id")
        else:
            raise Exception(f"Failed to create conversation: {response.status_code}")


# Singleton instance
claude_service = ClaudeService()