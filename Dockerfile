FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic python-multipart tiktoken

# Copy application code
COPY api/ ./api/
COPY services/ ./services/
COPY utils/ ./utils/
COPY main.py .

# Create config directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]