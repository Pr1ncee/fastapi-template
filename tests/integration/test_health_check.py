import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(async_test_client):
    response = await async_test_client.get("/api/v1/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Success"}
