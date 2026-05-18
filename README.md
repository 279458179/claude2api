# Claude2API

Reverse proxy for Claude web version to OpenAI-compatible API.

Convert Claude's web interface into a standard API format compatible with OpenAI's API specification.

## Features

- OpenAI-compatible API endpoints
- Support for streaming responses
- Account pool management
- Proxy support
- Multiple Claude models

## Requirements

- Python 3.10+
- Claude.ai session key (from browser cookies)

## Getting Session Key

1. Login to [claude.ai](https://claude.ai) in your browser
2. Open Developer Tools (F12) -> Application -> Cookies
3. Find the `sessionKey` cookie value
4. Copy the value and add it to `config.json`

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude2api.git
cd claude2api

# Install dependencies
pip install -e .

# Or use uv
uv sync
```

## Configuration

Edit `config.json`:

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

## Running

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
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

## Docker

```bash
docker build -t claude2api .
docker run -p 8000:8000 claude2api
```

## Disclaimer

This project is for personal learning and technical research purposes only. Use at your own risk. Account bans may occur.

## License

MIT License