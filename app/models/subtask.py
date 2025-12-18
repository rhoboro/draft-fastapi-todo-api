from uuid import UUID

from pydantic import Field

from .base import BaseModel, UTCDatetime
from .enums import Status


class SubTask(BaseModel):
    subtask_id: UUID
    title: str = Field(min_length=1, max_length=256)
    status: Status
    todo_id: UUID
    updated_at: UTCDatetime
