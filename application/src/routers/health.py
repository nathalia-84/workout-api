from fastapi import APIRouter

from src.services.health_service import get_health

router = APIRouter()


@router.get("/health")
async def health_check():
    return get_health()
