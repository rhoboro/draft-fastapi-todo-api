from uuid import UUID

from pydantic import Field

from .base import BaseModel, UTCDatetime
from .enums import Status
from .subtask import SubTask


class Todo(BaseModel):
    todo_id: UUID
    title: str = Field(min_length=1, max_length=256)
    status: Status
    updated_at: UTCDatetime
    subtask_count: int


class TodoWithSubTasks(Todo):
    subtasks: list[SubTask] | None = None
