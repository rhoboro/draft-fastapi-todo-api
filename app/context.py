from typing import Annotated
from uuid import UUID

import structlog
from fastapi import Path


async def bind_todo_id(
    todo_id: Annotated[UUID, Path()],
) -> None:
    structlog.contextvars.bind_contextvars(
        todo_id=str(todo_id)
    )


async def bind_subtask_id(
    subtask_id: Annotated[UUID, Path()],
) -> None:
    structlog.contextvars.bind_contextvars(
        subtask_id=str(subtask_id)
    )
