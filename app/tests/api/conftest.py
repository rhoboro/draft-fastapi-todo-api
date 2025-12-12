from collections.abc import Awaitable, Callable, Iterator
from datetime import datetime
from uuid import UUID

import pytest

from app.database import AsyncSession
from app.models import (
    Base,
    Status,
    SubTaskModel,
    TodoModel,
)


@pytest.fixture()
def common_dataset_datetime() -> Iterator[datetime]:
    yield datetime.fromisoformat("2025-12-14T10:20:30.839088Z")


@pytest.fixture()
def common_dataset(
    common_dataset_datetime: datetime,
) -> list[Base]:
    todo1 = TodoModel(
        todo_id=UUID("fa4fa0f5-2847-475f-ba67-76f4d8fa8a00"),
        title="Todo 1",
        status=Status.NEW,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )
    todo2 = TodoModel(
        todo_id=UUID("63efd7b7-b825-4b8d-b60a-728bb94dd90b"),
        title="Todo 2",
        status=Status.IN_PROGRESS,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )
    todo3 = TodoModel(
        todo_id=UUID("8940b5c4-57ac-4e38-8af4-82a510738717"),
        title="Todo 3",
        status=Status.COMPLETED,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )

    subtask1 = SubTaskModel(
        todo_id=todo1.todo_id,
        subtask_id=UUID(
            "3ae37426-2028-483c-b54d-079c4d9fc2a6"
        ),
        title="SubTask 1",
        status=Status.NEW,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )
    subtask2 = SubTaskModel(
        todo_id=todo2.todo_id,
        subtask_id=UUID(
            "093404d4-d5ac-4a05-b6b2-092a255273a4"
        ),
        title="SubTask 2",
        status=Status.IN_PROGRESS,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )
    subtask3 = SubTaskModel(
        todo_id=todo2.todo_id,
        subtask_id=UUID(
            "6bd784d7-9f84-412e-887d-dc1d95e64049"
        ),
        title="SubTask 3",
        status=Status.IN_PROGRESS,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )
    subtask4 = SubTaskModel(
        todo_id=todo3.todo_id,
        subtask_id=UUID(
            "bed229af-a244-4e56-9fd9-d6104255f4b1"
        ),
        title="SubTask 4",
        status=Status.COMPLETED,
        created_at=common_dataset_datetime,
        updated_at=common_dataset_datetime,
    )

    return [
        todo1,
        todo2,
        todo3,
        subtask1,
        subtask2,
        subtask3,
        subtask4,
    ]


@pytest.fixture()
async def insert(
    test_session: AsyncSession,
) -> Callable[[list[Base]], Awaitable[None]]:
    async def bulk_create(data: list[Base]) -> None:
        async with test_session.begin() as session:
            session.add_all(data)
            await session.commit()

    return bulk_create


@pytest.fixture()
async def setup_common_dataset(
    insert: Callable[[list[Base]], Awaitable[None]],
    common_dataset: list[Base],
) -> None:
    return await insert(common_dataset)
