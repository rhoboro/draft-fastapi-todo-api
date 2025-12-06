from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def ac() -> AsyncIterator[AsyncClient]:
    headers = {"APP-API-KEY": "DUMMY-KEY"}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://test.invalid",
        headers=headers,
    ) as c:
        yield c
