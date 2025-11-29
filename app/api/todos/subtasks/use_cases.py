from uuid import UUID, uuid4

from app.models import Status, SubTask
from app.utils.datetime import utcnow


class ListSubTasks:
    async def execute(
        self,
        todo_id: UUID,
    ) -> list[SubTask]:
        return []


class CreateSubTask:
    async def execute(
        self, todo_id: UUID, title: str
    ) -> SubTask:
        return SubTask(
            subtask_id=uuid4(),
            todo_id=todo_id,
            title=title,
            status=Status.NEW,
            updated_at=utcnow(),
        )


class GetSubTask:
    async def execute(
        self, todo_id: UUID, subtask_id: UUID
    ) -> SubTask:
        return SubTask(
            subtask_id=subtask_id,
            todo_id=todo_id,
            title="SubTask 1",
            status=Status.NEW,
            updated_at=utcnow(),
        )


class UpdateSubTask:
    async def execute(
        self,
        todo_id: UUID,
        subtask_id: UUID,
        title: str,
        status: Status,
    ) -> SubTask:
        return SubTask(
            todo_id=todo_id,
            subtask_id=subtask_id,
            title=title,
            status=status,
            updated_at=utcnow(),
        )


class DeleteSubTask:
    async def execute(
        self,
        todo_id: UUID,
        subtask_id: UUID,
    ) -> None:
        return None
