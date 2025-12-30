from uuid import UUID

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app import db
from app.database import AsyncSession
from app.models import Status
from app.utils.datetime import utcnow


@pytest.mark.anyio
@pytest.mark.usefixtures("setup_common_dataset")
async def test_list_todos(
    ac: AsyncClient,
) -> None:
    response = await ac.get("/api/todos")
    actual = response.json()
    assert actual == {
        "count": 3,
        "next": None,
        "previous": None,
        "todos": [
            {
                "status": "NEW",
                "title": "Todo 1",
                "todo_id": "fa4fa0f5-2847-475f-ba67-76f4d8fa8a00",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 1,
                "subtasks": None,
            },
            {
                "status": "IN_PROGRESS",
                "title": "Todo 2",
                "todo_id": "63efd7b7-b825-4b8d-b60a-728bb94dd90b",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 2,
                "subtasks": None,
            },
            {
                "status": "COMPLETED",
                "title": "Todo 3",
                "todo_id": "8940b5c4-57ac-4e38-8af4-82a510738717",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 1,
                "subtasks": None,
            },
        ],
    }


@pytest.mark.anyio
@pytest.mark.usefixtures("setup_common_dataset")
async def test_list_todos_include_subtasks(
    ac: AsyncClient,
) -> None:
    response = await ac.get(
        "/api/todos",
        params={"include_subtasks": True},
    )
    actual = response.json()
    assert actual == {
        "count": 3,
        "next": None,
        "previous": None,
        "todos": [
            {
                "status": "NEW",
                "title": "Todo 1",
                "todo_id": "fa4fa0f5-2847-475f-ba67-76f4d8fa8a00",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 1,
                "subtasks": [
                    {
                        "status": "NEW",
                        "subtask_id": "3ae37426-2028-483c-b54d-079c4d9fc2a6",  # noqa: E501
                        "title": "SubTask 1",
                        "todo_id": "fa4fa0f5-2847-475f-ba67-76f4d8fa8a00",  # noqa: E501
                        "updated_at": "2025-12-14T10:20:30.839088Z",  # noqa: E501
                    },
                ],
            },
            {
                "status": "IN_PROGRESS",
                "title": "Todo 2",
                "todo_id": "63efd7b7-b825-4b8d-b60a-728bb94dd90b",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 2,
                "subtasks": [
                    {
                        "status": "IN_PROGRESS",
                        "subtask_id": "093404d4-d5ac-4a05-b6b2-092a255273a4",  # noqa: E501
                        "title": "SubTask 2",
                        "todo_id": "63efd7b7-b825-4b8d-b60a-728bb94dd90b",  # noqa: E501
                        "updated_at": "2025-12-14T10:20:30.839088Z",  # noqa: E501
                    },
                    {
                        "status": "IN_PROGRESS",
                        "subtask_id": "6bd784d7-9f84-412e-887d-dc1d95e64049",  # noqa: E501
                        "title": "SubTask 3",
                        "todo_id": "63efd7b7-b825-4b8d-b60a-728bb94dd90b",  # noqa: E501
                        "updated_at": "2025-12-14T10:20:30.839088Z",  # noqa: E501
                    },
                ],
            },
            {
                "status": "COMPLETED",
                "title": "Todo 3",
                "todo_id": "8940b5c4-57ac-4e38-8af4-82a510738717",  # noqa: E501
                "updated_at": "2025-12-14T10:20:30.839088Z",
                "subtask_count": 1,
                "subtasks": [
                    {
                        "status": "COMPLETED",
                        "subtask_id": "bed229af-a244-4e56-9fd9-d6104255f4b1",  # noqa: E501
                        "title": "SubTask 4",
                        "todo_id": "8940b5c4-57ac-4e38-8af4-82a510738717",  # noqa: E501
                        "updated_at": "2025-12-14T10:20:30.839088Z",  # noqa: E501
                    },
                ],
            },
        ],
    }


@pytest.mark.anyio
@pytest.mark.usefixtures("test_session")
async def test_create_todo(
    ac: AsyncClient,
    test_session: AsyncSession,
    mocker: MockerFixture,
) -> None:
    datetime_now = utcnow()
    todo_id = UUID("ccc92566-d062-4a43-83a2-bbb05962a49e")
    mocker.patch(
        "app.api.todos.use_cases.uuid4",
        lambda: todo_id,
    )

    response = await ac.post(
        "/api/todos", json={"title": "new todo"}
    )
    actual = response.json()
    assert actual == {
        "todo_id": "ccc92566-d062-4a43-83a2-bbb05962a49e",
        "title": "new todo",
        "status": "NEW",
        "subtask_count": 0,
        "updated_at": "2025-12-15T20:40:50.839088Z",
    }
    assert response.status_code == 201

    # レコードが追加されたことも確認
    async with test_session() as session:
        record = await db.Todo.get_by_id(
            session, todo_id=todo_id
        )
        assert record is not None
        assert record.title == "new todo"
        assert record.status == Status.NEW
        assert record.created_at == datetime_now
        assert record.updated_at == datetime_now
        assert await record.awaitable_attrs.subtasks == []


@pytest.mark.anyio
@pytest.mark.usefixtures("setup_common_dataset")
async def test_update_todo_not_found(
    ac: AsyncClient,
) -> None:
    todo_id = "00000000-0000-0000-0000-000000000000"
    response = await ac.put(
        f"/api/todos/{todo_id}",
        json={
            "title": "new todo",
            "status": "IN_PROGRESS",
        },
    )
    actual = response.json()
    assert actual == {
        "details": {
            "Todo": "00000000-0000-0000-0000-000000000000"
        },
        "message": "Not Found",
    }
    assert response.status_code == 404
