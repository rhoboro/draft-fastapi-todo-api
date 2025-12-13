from datetime import datetime
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from app.api.todos.use_cases import CreateTodo, GetTodo
from app.database import AsyncSession
from app.exceptions import NotFound
from app.models import Status, Todo, TodoModel
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
            updated_at=datetime_now,
        )
        assert actual == expected

        # レコードが追加されたことも確認
        async with test_session() as session:
            record = await TodoModel.get_by_id(
                session, todo_id=todo_id
            )
            assert record is not None
            assert record.title == "new todo"
            assert record.status == Status.NEW
            assert record.created_at == datetime_now
            assert record.updated_at == datetime_now
            assert await record.awaitable_attrs.subtasks == []
