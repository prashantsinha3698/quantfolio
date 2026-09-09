"""
Health check and environment status endpoint.
"""
from datetime import datetime
from fastapi import APIRouter
from app.core.config import PROJECT_NAME, VERSION

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": PROJECT_NAME,
        "version": VERSION,
        "timestamp": datetime.now().isoformat(),
    }
