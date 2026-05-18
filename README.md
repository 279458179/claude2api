# Claude2API

将 Claude 网页版转换为 OpenAI 兼容的 API 接口。

## 功能特性

- OpenAI 兼容 API 接口
- 支持流式响应 (SSE)
- 账号池管理
- 代理支持
- Docker 一键部署

## 快速开始

### 1. 获取 Session Key

1. 登录 [claude.ai](https://claude.ai)
2. 按 `F12` 打开开发者工具
3. 切换到 `Application` 标签页
4. 展开 `Cookies` -> 点击 `https://claude.ai`
5. 找到 `sessionKey` 字段，复制其值

### 2. Docker 部署

```bash
# 克隆项目
git clone https://github.com/279458179/claude2api.git
cd claude2api

# 创建配置目录
mkdir -p data
cp config.example.json data/config.json

# 编辑配置文件，添加 session_key
vim data/config.json

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

服务将在 `http://localhost:8001` 启动。

### 3. 配置说明

#### 单账号配置

编辑 `data/config.json`：

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

#### 多账号配置

在 `accounts` 数组中添加多个账号即可：

```json
{
    "accounts": [
        {
            "session_key": "SESSION_KEY_1",
            "name": "Account 1",
            "active": true
        },
        {
            "session_key": "SESSION_KEY_2",
            "name": "Account 2",
            "active": true
        },
        {
            "session_key": "SESSION_KEY_3",
            "name": "Account 3",
            "active": false
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

**多账号负载均衡说明**：
- 系统自动使用第一个 `active: true` 的账号
- 如需指定特定账号，在请求头中传入 `Authorization: Bearer <session_key>`
- 某账号失效时，可设置 `active: false` 暂时禁用

**指定账号请求示例**：
```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SESSION_KEY_2" \
  -d '{"model": "claude-sonnet-4-20250514", "messages": [{"role": "user", "content": "Hello"}]}'
```

#### 配置字段说明

| 字段 | 说明 |
|------|------|
| `session_key` | Claude.ai 的 sessionKey cookie 值 |
| `name` | 账号名称（可选，便于识别） |
| `active` | 是否启用该账号（`true`/`false`） |
| `proxy.enabled` | 是否启用代理 |
| `proxy.http/https` | 代理地址 |

---

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8001/v1`
- **Content-Type**: `application/json`
- **认证方式**: Bearer Token（可选，用于指定特定账号）

### 1. 获取模型列表

**请求**
```
GET /v1/models
```

**示例**
```bash
curl http://localhost:8001/v1/models
```

**响应**
```json
{
    "object": "list",
    "data": [
        {
            "id": "claude-sonnet-4-20250514",
            "object": "model",
            "created": 1715000000,
            "owned_by": "anthropic"
        },
        {
            "id": "claude-opus-4-20250514",
            "object": "model",
            "created": 1715000000,
            "owned_by": "anthropic"
        }
    ]
}
```

### 2. 聊天补全 (Chat Completions)

**请求**
```
POST /v1/chat/completions
```

**请求体参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称 |
| `messages` | array | 是 | 消息列表 |
| `stream` | boolean | 否 | 是否流式输出，默认 false |
| `temperature` | float | 否 | 温度参数 (0-1) |
| `max_tokens` | int | 否 | 最大输出 token 数 |

**messages 格式**
```json
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
]
```

**非流式请求示例**
```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [
      {"role": "user", "content": "Hello, Claude!"}
    ]
  }'
```

**非流式响应**
```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1715000000,
    "model": "claude-sonnet-4-20250514",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}
```

**流式请求示例**
```bash
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [
      {"role": "user", "content": "Hello, Claude!"}
    ],
    "stream": true
  }'
```

**流式响应 (SSE 格式)**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1715000000,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1715000000,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1715000000,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{"content":" How can I help you?"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1715000000,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### 3. 账号管理

**获取账号列表**
```
GET /v1/accounts
```

```bash
curl http://localhost:8001/v1/accounts
```

**响应**
```json
{
    "accounts": [
        {
            "account_id": "acc_1",
            "name": "My Account",
            "email": null,
            "active": true
        }
    ]
}
```

**添加账号**
```
POST /v1/accounts
```

```bash
curl http://localhost:8001/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "session_key": "YOUR_NEW_SESSION_KEY",
    "name": "Account 2"
  }'
```

**激活/停用账号**
```
POST /v1/accounts/{account_id}/activate
POST /v1/accounts/{account_id}/deactivate
```

```bash
curl -X POST http://localhost:8001/v1/accounts/acc_1/deactivate
curl -X POST http://localhost:8001/v1/accounts/acc_1/activate
```

**删除账号**
```
DELETE /v1/accounts/{account_id}
```

```bash
curl -X DELETE http://localhost:8001/v1/accounts/acc_1
```

### 4. 系统接口

**健康检查**
```
GET /v1/system/health
```

```bash
curl http://localhost:8001/v1/system/health
```

**响应**
```json
{"status": "ok"}
```

**系统信息**
```
GET /v1/system/info
```

```bash
curl http://localhost:8001/v1/system/info
```

---

## 支持的模型

| 模型 ID | 说明 |
|---------|------|
| `claude-sonnet-4-20250514` | Claude Sonnet 4 |
| `claude-opus-4-20250514` | Claude Opus 4 |
| `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet |
| `claude-3-5-haiku-20241022` | Claude 3.5 Haiku |

---

## 使用示例

### Python (OpenAI SDK)

```python
import openai

client = openai.OpenAI(
    api_key="any",  # 可忽略，或传入 session_key 指定账号
    base_url="http://localhost:8001/v1"
)

# 非流式
response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)
print(response.choices[0].message.content)

# 流式
response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ],
    stream=True
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Python (httpx)

```python
import httpx
import json

# 非流式
response = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "claude-sonnet-4-20250514",
        "messages": [{"role": "user", "content": "Hello!"}]
    }
)
print(response.json()["choices"][0]["message"]["content"])

# 流式
with httpx.stream(
    "POST",
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "claude-sonnet-4-20250514",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": True
    }
) as response:
    for line in response.iter_lines():
        if line.startswith("data: ") and line != "data: [DONE]":
            data = json.loads(line[6:])
            content = data["choices"][0]["delta"].get("content")
            if content:
                print(content, end="", flush=True)
```

### JavaScript / Node.js

```javascript
const response = await fetch('http://localhost:8001/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        messages: [{ role: 'user', content: 'Hello!' }],
        stream: true
    })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    for (const line of lines) {
        if (line.startsWith('data: ') && line !== 'data: [DONE]') {
            const data = JSON.parse(line.slice(6));
            const content = data.choices[0]?.delta?.content;
            if (content) console.log(content);
        }
    }
}
```

### curl 测试

```bash
# 测试健康检查
curl http://localhost:8001/v1/system/health

# 测试模型列表
curl http://localhost:8001/v1/models

# 测试聊天（非流式）
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-20250514", "messages": [{"role": "user", "content": "Say hello in 3 languages"}]}'

# 测试聊天（流式）
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-20250514", "messages": [{"role": "user", "content": "Count from 1 to 10"}], "stream": true}'
```

---

## 错误处理

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | 未授权（未配置账号或 session_key 无效） |
| 500 | 内部错误 |

**错误响应格式**
```json
{
    "error": {
        "message": "Error description",
        "type": "internal_error"
    }
}
```

---

## 非Docker部署

```bash
# 安装依赖
pip install fastapi uvicorn httpx pydantic python-multipart tiktoken

# 克隆项目
git clone https://github.com/279458179/claude2api.git
cd claude2api

# 配置
cp config.example.json config.json
vim config.json  # 添加 session_key

# 运行
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 注意事项

- 本项目仅供学习研究使用
- 使用网页版 API 可能导致账号被封禁，请谨慎使用
- session_key 有效期有限，可能需要定期更新
- 建议配置多个账号作为备用

---

## License

MIT License