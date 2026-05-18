FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic python-multipart tiktoken

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]