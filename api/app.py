from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .ai import router as ai_router
from .accounts import router as accounts_router
from .system import router as system_router
from .admin import router as admin_router
from services.config import config
from services.claude_service import claude_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config.load()
    await claude_service.init_sessions()
    yield
    # Shutdown
    await claude_service.close_sessions()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Claude2API",
        description="Reverse proxy for Claude web version to OpenAI-compatible API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(ai_router, prefix="/v1", tags=["AI"])
    app.include_router(accounts_router, prefix="/v1/accounts", tags=["Accounts"])
    app.include_router(system_router, prefix="/v1/system", tags=["System"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(exc), "type": "internal_error"}}
        )

    return app