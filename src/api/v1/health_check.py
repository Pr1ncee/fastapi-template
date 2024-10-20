from fastapi import APIRouter

router = APIRouter(tags=["health-check"])


@router.get("/health-check/")
async def get_health_check_status():
    return {"status": "Success"}
