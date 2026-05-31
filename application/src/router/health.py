from fastapi import APIRouter

from src.service.health_service import get_health

router = APIRouter()


@router.get("/health")
async def health_check():
    return get_health()
