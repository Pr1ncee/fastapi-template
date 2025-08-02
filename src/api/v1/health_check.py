from fastapi import APIRouter

router = APIRouter(tags=["health-check"])


@router.get("/health-check/")
async def get_health_check_status() -> dict[str, str]:
    return {"status": "Success"}
