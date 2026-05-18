from .app import create_app
from .ai import router as ai_router
from .accounts import router as accounts_router
from .system import router as system_router

__all__ = ["create_app"]