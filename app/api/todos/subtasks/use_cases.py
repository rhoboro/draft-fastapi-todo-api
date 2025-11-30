from uuid import UUID, uuid4

from app.database import AsyncSession
from app.exceptions import NotFound
from app.models import Status, SubTask, SubTaskModel, TodoModel


class ListSubTasks:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
    ) -> list[SubTask]:
        async with self.session() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)

            subtasks = await SubTaskModel.get_all_by_todo(
                session, todo
            )
            return [
                SubTask.model_validate(todo)
                async for todo in subtasks
            ]


class CreateSubTask:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self, todo_id: UUID, title: str
    ) -> SubTask:
        async with self.session.begin() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)

            subtask = await SubTaskModel.create(
                session,
                todo=todo,
                subtask_id=uuid4(),
                title=title,
                status=Status.NEW,
            )
            return SubTask.model_validate(subtask)


class GetSubTask:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self, todo_id: UUID, subtask_id: UUID
    ) -> SubTask:
        async with self.session() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)

            subtask = await SubTaskModel.get_by_id(
                session, todo, subtask_id
            )
            if not subtask:
                raise NotFound("SubTask", subtask_id)
            return SubTask.model_validate(subtask)


class UpdateSubTask:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
        subtask_id: UUID,
        title: str,
        status: Status,
    ) -> SubTask:
        async with self.session.begin() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)

            subtask = await SubTaskModel.get_by_id(
                session, todo, subtask_id
            )
            if not subtask:
                raise NotFound("SubTask", subtask_id)

            await subtask.update(
                session,
                todo=todo,
                title=title,
                status=status,
            )
            return SubTask.model_validate(subtask)


class DeleteSubTask:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
        subtask_id: UUID,
    ) -> None:
        async with self.session.begin() as session:
            todo = await TodoModel.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)
            subtask = await SubTaskModel.get_by_id(
                session, todo, subtask_id
            )
            if not subtask:
                return
            await SubTaskModel.delete(session, subtask)
