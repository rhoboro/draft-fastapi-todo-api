import io
from asyncio import TaskGroup
from datetime import datetime
from uuid import UUID

import pytest
from fastapi import BackgroundTasks, UploadFile
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app import db
from app.api.todos.use_cases import (
    CreateTodo,
    GetTodo,
    ImportTodos,
)
from app.api.todos.webhook import WebhookClient
from app.database import AsyncSession
from app.exceptions import NotFound
from app.models import Status, Todo
from app.utils.datetime import utcnow


@pytest.mark.anyio
@pytest.mark.usefixtures("setup_common_dataset")
class TestGetTodo:
    async def test_execute(
        self,
        test_session: AsyncSession,
        common_dataset_datetime: datetime,
    ) -> None:
        use_case = GetTodo(session=test_session)
        todo_id = UUID("fa4fa0f5-2847-475f-ba67-76f4d8fa8a00")
        # 処理の実行
        actual = await use_case.execute(
            todo_id=todo_id,
        )
        expected = Todo(
            todo_id=todo_id,
            title="Todo 1",
            status=Status.NEW,
            subtask_count=1,
            updated_at=common_dataset_datetime,
        )
        assert actual == expected

    async def test_execute_not_found(
        self, test_session: AsyncSession
    ) -> None:
        use_case = GetTodo(session=test_session)
        # 例外NotFoundが送出されたらテスト成功
        with pytest.raises(NotFound):
            await use_case.execute(
                todo_id=UUID(
                    "00000000-0000-0000-0000-000000000000"
                ),
            )


@pytest.mark.anyio
@pytest.mark.usefixtures("setup_common_dataset")
class TestCreateTodo:
    async def test_execute(
        self,
        test_session: AsyncSession,
        mocker: MockerFixture,
    ) -> None:
        datetime_now = utcnow()
        todo_id = UUID("ccc92566-d062-4a43-83a2-bbb05962a49e")
        mocker.patch(
            "app.api.todos.use_cases.uuid4",
            lambda: todo_id,
        )

        use_case = CreateTodo(session=test_session)
        actual = await use_case.execute(title="new todo")
        assert actual is not None

        expected = Todo(
            todo_id=todo_id,
            title="new todo",
            status=Status.NEW,
            subtask_count=0,
            updated_at=datetime_now,
        )
        assert actual == expected

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
class TestImportTodos:
    async def test_import_todos(
        self,
        test_session: AsyncSession,
    ) -> None:
        use_case = ImportTodos(
            session=test_session,
            background_tasks=BackgroundTasks(),
            webhook=WebhookClient(AsyncClient(), TaskGroup()),
        )
        file = UploadFile(
            io.BytesIO(
                """title,status
Todo 1,NEW
Todo 2,IN_PROGRESS
""".encode("utf-8")
            ),
        )
        new_todos, new_subtasks = await use_case.import_todos(
            file
        )
        assert len(new_todos) == 2
        assert new_todos[0].title == "Todo 1"
        assert new_todos[0].status == Status.NEW
        assert new_todos[1].title == "Todo 2"
        assert new_todos[1].status == Status.IN_PROGRESS
        assert len(new_subtasks) == 0

    async def test_import_todos_chunk(
        self,
        test_session: AsyncSession,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch("app.db.todo.BULK_SIZE_LIMIT", 2)
        use_case = ImportTodos(
            session=test_session,
            background_tasks=BackgroundTasks(),
            webhook=WebhookClient(AsyncClient(), TaskGroup()),
        )
        file = UploadFile(
            io.BytesIO(
                """title,status,subtask_title,subtask_status
Todo 1,NEW
,,SubTask 11,NEW
,,SubTask 12,NEW
Todo 2,IN_PROGRESS
,,SubTask 21,COMPLETED
,,SubTask 22,IN_PROGRESS
,,SubTask 23,NEW
Todo 3,COMPLETED
""".encode("utf-8")
            ),
        )
        new_todos, new_subtasks = await use_case.import_todos(
            file
        )
        assert len(new_todos) == 3
        assert len(new_subtasks) == 5

        # Todo 1
        assert new_todos[0].title == "Todo 1"
        assert new_todos[0].status == Status.NEW
        assert new_subtasks[0].todo_id == new_todos[0].todo_id
        assert new_subtasks[0].title == "SubTask 11"
        assert new_subtasks[0].status == Status.NEW
        assert new_subtasks[1].todo_id == new_todos[0].todo_id
        assert new_subtasks[1].title == "SubTask 12"
        assert new_subtasks[1].status == Status.NEW

        # Todo 2
        assert new_todos[1].title == "Todo 2"
        assert new_todos[1].status == Status.IN_PROGRESS
        assert new_subtasks[2].todo_id == new_todos[1].todo_id
        assert new_subtasks[2].title == "SubTask 21"
        assert new_subtasks[2].status == Status.COMPLETED
        assert new_subtasks[3].todo_id == new_todos[1].todo_id
        assert new_subtasks[3].title == "SubTask 22"
        assert new_subtasks[3].status == Status.IN_PROGRESS
        assert new_subtasks[4].todo_id == new_todos[1].todo_id
        assert new_subtasks[4].title == "SubTask 23"
        assert new_subtasks[4].status == Status.NEW

        # Todo 3
        assert new_todos[2].title == "Todo 3"
        assert new_todos[2].status == Status.COMPLETED
