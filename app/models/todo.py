from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Self
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)

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

    @classmethod
    async def get_all(
        cls, session: AsyncSession
    ) -> AsyncIterator[Self]:
        stmt = (
            select(cls)
            .options(selectinload(cls.subtasks))
            .order_by(desc(cls.created_at))
        )
        return await session.stream_scalars(stmt)

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        todo_id: UUID,
    ) -> Self | None:
        stmt = select(cls).where(cls.todo_id == todo_id)
        todo = await session.scalar(stmt)
        return todo

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        todo_id: UUID,
        title: str,
        status: Status,
    ) -> Self:
        todo = cls(
            todo_id=todo_id,
            title=title,
            status=status,
            subtasks=[],
        )
        session.add(todo)
        await session.flush()
        return todo

    async def update(
        self,
        session: AsyncSession,
        title: str,
        status: Status,
    ) -> Self:
        self.title = title
        self.status = status
        await session.flush()
        return self

    @classmethod
    async def delete(
        cls, session: AsyncSession, todo: Self
    ) -> None:
        await session.delete(todo)
        await session.flush()
