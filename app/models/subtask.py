from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, str_256
from .enums import Status

if TYPE_CHECKING:
    from .todo import TodoModel


class SubTaskModel(Base):
    __tablename__ = "subtasks"

    subtask_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    status: Mapped[Status]
    todo_id: Mapped[UUID] = mapped_column(
        ForeignKey("todos.todo_id"), index=True
    )
    todo: Mapped["TodoModel"] = relationship(
        back_populates="subtasks",
    )
