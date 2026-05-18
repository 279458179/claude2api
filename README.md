# Claude2API

Reverse proxy for Claude web version to OpenAI-compatible API.

Convert Claude's web interface into a standard API format compatible with OpenAI's API specification.

## Features

- OpenAI-compatible API endpoints
- Support for streaming responses
- Account pool management
- Proxy support
- Multiple Claude models
- Docker deployment

## Requirements

- Docker and Docker Compose
- Claude.ai session key (from browser cookies)

## Getting Session Key

1. Login to [claude.ai](https://claude.ai) in your browser
2. Open Developer Tools (F12) -> Application -> Cookies
3. Find the `sessionKey` cookie value
4. Copy the value and add it to `config.json`

## Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/279458179/claude2api.git
cd claude2api

# Create config directory
mkdir -p data

# Copy example config
cp config.example.json data/config.json

# Edit config.json and add your session_key
# Then start the service
docker compose up -d
```

The API will be available at `http://localhost:8000`.

## Configuration

Edit `data/config.json`:

```json
{
    "accounts": [
        {
            "session_key": "YOUR_SESSION_KEY_HERE",
            "name": "My Account",
            "active": true
        }
    ],
    "proxy": {
        "enabled": false,
        "http": "",
        "https": ""
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000
    }
}
```

## Docker Commands

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop service
docker compose down

# Restart service
docker compose restart
```

## API Endpoints

### List Models
```
GET /v1/models
```

### Chat Completions
```
POST /v1/chat/completions
```

Request body:
```json
{
    "model": "claude-sonnet-4-20250514",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "stream": true
}
```

### Account Management
```
GET /v1/accounts
POST /v1/accounts
DELETE /v1/accounts/{account_id}
```

### System
```
GET /v1/system/health
GET /v1/system/info
```

## Supported Models

- `claude-sonnet-4-20250514`
- `claude-opus-4-20250514`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

## Usage Example

```python
import openai

client = openai.OpenAI(
    api_key="your_session_key",  # Optional: use specific account
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

## Manual Installation (Non-Docker)

```bash
pip install fastapi uvicorn httpx pydantic python-multipart tiktoken

# Copy config
cp config.example.json config.json

# Edit config.json and add your session_key

# Run
python main.py
```

## Disclaimer

This project is for personal learning and technical research purposes only. Use at your own risk. Account bans may occur.

## License

MIT License
