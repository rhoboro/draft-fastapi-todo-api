from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel as _BaseModel
from pydantic import BeforeValidator, ConfigDict, Field

from app.utils.datetime import to_utc

from .enums import Status

UTCDatetime = Annotated[datetime, BeforeValidator(to_utc)]


class BaseSchema(_BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class Todo(BaseSchema):
    todo_id: UUID
    title: str = Field(min_length=1, max_length=256)
    status: Status
    updated_at: UTCDatetime


class SubTask(BaseSchema):
    subtask_id: UUID
    title: str = Field(min_length=1, max_length=256)
    status: Status
    todo_id: UUID
    updated_at: UTCDatetime
