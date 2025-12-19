from uuid import UUID

from pydantic import Field

from .base import BaseModel, UTCDatetime
from .enums import Status


class Todo(BaseModel):
    todo_id: UUID
    title: str = Field(min_length=1, max_length=256)
    status: Status
    updated_at: UTCDatetime
