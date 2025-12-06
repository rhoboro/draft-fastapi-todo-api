from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.exceptions import NotFound, init_exception_handler


@pytest.fixture
async def ac() -> AsyncIterator[AsyncClient]:
    app = FastAPI()
    init_exception_handler(app)

    @app.get("/_test/not_found/{resource_id}")
    async def not_found(resource_id: UUID) -> None:
        raise NotFound("Resource", resource_id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test.invalid",
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_resource_not_found(ac: AsyncClient) -> None:
    resource_id = "00000000-0000-0000-0000-000000000000"
    response = await ac.get(f"/_test/not_found/{resource_id}")
    assert response.status_code == 404

    expected = {
        "details": {
            "Resource": "00000000-0000-0000-0000-000000000000"
        },
        "message": "Not Found",
    }
    assert response.json() == expected
