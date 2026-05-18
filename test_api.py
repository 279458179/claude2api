"""
Test script for claude2api
Run this after starting the server: python main.py
"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/system/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200


async def test_models():
    """Test models endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/models")
        print(f"Models: {response.status_code} - {response.json()}")
        return response.status_code == 200


async def test_accounts():
    """Test accounts endpoints"""
    async with httpx.AsyncClient() as client:
        # List accounts
        response = await client.get(f"{BASE_URL}/v1/accounts")
        print(f"List accounts: {response.status_code} - {response.json()}")

        # Add account
        response = await client.post(
            f"{BASE_URL}/v1/accounts",
            json={"session_key": "test_key_123", "name": "Test Account"}
        )
        print(f"Add account: {response.status_code} - {response.json()}")

        # List again
        response = await client.get(f"{BASE_URL}/v1/accounts")
        data = response.json()
        print(f"List accounts after add: {response.status_code} - {data}")

        if data.get("accounts"):
            account_id = data["accounts"][0]["account_id"]

            # Deactivate
            response = await client.post(f"{BASE_URL}/v1/accounts/{account_id}/deactivate")
            print(f"Deactivate: {response.status_code} - {response.json()}")

            # Activate
            response = await client.post(f"{BASE_URL}/v1/accounts/{account_id}/activate")
            print(f"Activate: {response.status_code} - {response.json()}")

            # Delete
            response = await client.delete(f"{BASE_URL}/v1/accounts/{account_id}")
            print(f"Delete: {response.status_code} - {response.json()}")

        return True


async def test_chat_without_account():
    """Test chat without account - should fail"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        print(f"Chat without account: {response.status_code} - {response.json()}")
        return response.status_code == 401


async def main():
    print("=" * 50)
    print("Testing claude2api")
    print("=" * 50)

    tests = [
        ("Health check", test_health),
        ("Models", test_models),
        ("Accounts", test_accounts),
        ("Chat without account", test_chat_without_account),
    ]

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = await test_func()
            status = "[PASSED]" if result else "[FAILED]"
            print(f"Status: {status}")
        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())