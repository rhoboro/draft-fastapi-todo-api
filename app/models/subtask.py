from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Self
from uuid import UUID

from sqlalchemy import ForeignKey, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
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

    @classmethod
    async def get_all_by_todo(
        cls,
        session: AsyncSession,
        todo: "TodoModel",
    ) -> AsyncIterator[Self]:
        stmt = (
            select(cls)
            .where(cls.todo_id == todo.todo_id)
            .order_by(asc(cls.created_at))
        )
        return await session.stream_scalars(stmt)

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        todo: "TodoModel",
        subtask_id: UUID,
    ) -> Self | None:
        stmt = select(cls).where(
            cls.todo_id == todo.todo_id,
            cls.subtask_id == subtask_id,
        )
        subtask = await session.scalar(stmt)
        return subtask

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        todo: "TodoModel",
        subtask_id: UUID,
        title: str,
        status: Status,
    ) -> Self:
        subtask = cls(
            todo=todo,
            subtask_id=subtask_id,
            title=title,
            status=status,
        )
        session.add(subtask)
        await session.flush()
        await session.refresh(subtask)
        return subtask

    async def update(
        self,
        session: AsyncSession,
        todo: "TodoModel",
        title: str,
        status: Status,
    ) -> None:
        self.todo = todo
        self.title = title
        self.status = status
        await session.flush()

    @classmethod
    async def delete(
        cls, session: AsyncSession, subtask: Self
    ) -> None:
        await session.delete(subtask)
        await session.flush()
