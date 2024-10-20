from fastapi import APIRouter

from src.api.v1.health_check import router as health_check_router

router = APIRouter(prefix="/v1")

router.include_router(health_check_router)
