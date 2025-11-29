from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, str_256
from .enums import Status

if TYPE_CHECKING:
    from .subtask import SubTaskModel


class TodoModel(Base):
    __tablename__ = "todos"

    todo_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    status: Mapped[Status]

    subtasks: Mapped[list["SubTaskModel"]] = relationship(
        back_populates="todo",
        cascade="delete, delete-orphan",
    )
