from uuid import UUID, uuid4

from app.models import Status, Todo
from app.utils.datetime import utcnow


class ListTodos:
    async def execute(
        self,
    ) -> list[Todo]:
        return []


class CreateTodo:
    async def execute(self, title: str) -> Todo:
        return Todo(
            todo_id=uuid4(),
            title=title,
            status=Status.NEW,
            updated_at=utcnow(),
        )


class GetTodo:
    async def execute(self, todo_id: UUID) -> Todo:
        return Todo(
            todo_id=todo_id,
            title="Todo 1",
            status=Status.NEW,
            updated_at=utcnow(),
        )


class UpdateTodo:
    async def execute(
        self,
        todo_id: UUID,
        title: str,
        status: Status,
    ) -> Todo:
        return Todo(
            todo_id=todo_id,
            title=title,
            status=status,
            updated_at=utcnow(),
        )


class DeleteTodo:
    async def execute(
        self,
        todo_id: UUID,
    ) -> None:
        return None
