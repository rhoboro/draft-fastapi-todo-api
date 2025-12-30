from collections.abc import AsyncIterator, Iterable
from typing import TYPE_CHECKING, Self, TypedDict
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, asc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models import Status
from app.utils import get_chunk

from .base import Base, str_256

if TYPE_CHECKING:
    from .todo import Todo


class BulkSubTaskCreateParam(TypedDict):
    todo_id: UUID
    title: str
    status: Status


BULK_SIZE_LIMIT = 100


class SubTask(Base):
    __tablename__ = "subtasks"

    subtask_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    status: Mapped[Status]
    todo_id: Mapped[UUID] = mapped_column(
        ForeignKey("todos.todo_id"), index=True
    )
    todo: Mapped["Todo"] = relationship(
        back_populates="subtasks",
    )

    @classmethod
    async def get_all_by_todo(
        cls,
        session: AsyncSession,
        todo: "Todo",
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
        todo: "Todo",
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
        todo: "Todo",
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
        todo: "Todo",
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

    @classmethod
    async def bulk_create(
        cls,
        session: AsyncSession,
        subtasks: Iterable[BulkSubTaskCreateParam],
    ) -> list[Self]:
        return [
            records
            for chunk in get_chunk(subtasks, n=BULK_SIZE_LIMIT)
            for records in await cls._bulk_create(
                session, chunk
            )
        ]

    @classmethod
    async def _bulk_create(
        cls,
        session: AsyncSession,
        subtasks: Iterable[BulkSubTaskCreateParam],
    ) -> list[Self]:
        new_subtask_dict = [
            {
                "subtask_id": uuid4(),
                "todo_id": subtask["todo_id"],
                "title": subtask["title"],
                "status": subtask["status"],
            }
            for subtask in subtasks
        ]
        stmt = (
            insert(cls).values(new_subtask_dict).returning(cls)
        )
        return [
            subtask
            for subtask in (
                (await session.execute(stmt)).scalars()
            )
        ]
