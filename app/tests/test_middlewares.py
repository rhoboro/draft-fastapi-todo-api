import json
from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from app.middlewares import ProcessTimeMiddleware


@pytest.fixture
async def ac() -> AsyncIterator[AsyncClient]:
    app = FastAPI()
    app.add_middleware(ProcessTimeMiddleware)

    @app.get("/")
    async def index() -> dict[str, str]:
        return {"status": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test.invalid",
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_process_time_middleware(
    ac: AsyncClient,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    request_id = "00000000-0000-0000-0000-000000000000"
    mocker.patch(
        "app.middlewares.uuid4", lambda: UUID(request_id)
    )
    res = await ac.get("/", headers={})
    assert res.status_code == 200

    captured_log = json.loads(capsys.readouterr().out)

    assert "process_time" in captured_log
    assert captured_log["event"] == "canonical-log-line"
    assert captured_log["status_code"] == 200
    assert captured_log["method"] == "GET"
    assert captured_log["path"] == "/"
    assert captured_log["request_id"] == request_id
