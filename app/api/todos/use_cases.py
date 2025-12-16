from uuid import UUID, uuid4

from fastapi import BackgroundTasks, UploadFile

from app.database import AsyncSession
from app.exceptions import NotFound
from app.models import Status, Todo, TodoModel


class ListTodos:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
    ) -> list[Todo]:
        async with self.session() as session:
            todos = await TodoModel.get_all(session)
            return [
                Todo.model_validate(todo)
                async for todo in todos
            ]


class CreateTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, title: str) -> Todo:
        async with self.session.begin() as session:
            todo = await TodoModel.create(
                session,
                todo_id=uuid4(),
                title=title,
                status=Status.NEW,
            )
            return Todo.model_validate(todo)


class GetTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, todo_id: UUID) -> Todo:
        async with self.session() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)
            return Todo.model_validate(todo)


class UpdateTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
        title: str,
        status: Status,
    ) -> Todo:
        async with self.session.begin() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)
            await todo.update(session, title, status)
            return Todo.model_validate(todo)


class DeleteTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
    ) -> None:
        async with self.session.begin() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                return
            await TodoModel.delete(session, todo)


class ImportTodos:
    def __init__(
        self,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
    ) -> None:
        self.session = session
        self.background_tasks = background_tasks

    async def execute(self, file: UploadFile) -> UUID:
        operation_id = uuid4()
        return operation_id
