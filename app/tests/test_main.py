import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(ac: AsyncClient) -> None:
    response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "It worked!!"}
