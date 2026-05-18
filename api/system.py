from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@router.get("/info")
async def system_info():
    """Get system information"""
    from services.config import config
    return {
        "version": "0.1.0",
        "accounts_count": len(config.accounts),
        "proxy_enabled": config.proxy.get("enabled", False)
    }