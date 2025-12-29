from collections.abc import AsyncIterator, Iterable
from typing import TYPE_CHECKING, Self
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    noload,
    relationship,
)

from app.models import Status

from .base import Base, str_256

if TYPE_CHECKING:
    from app.db.subtask import SubTask

from typing import TypedDict
from uuid import uuid4

from sqlalchemy import insert

from app.utils import get_chunk


class BulkCreateParam(TypedDict):
    title: str
    status: Status


BULK_SIZE_LIMIT = 100


class Todo(Base):
    __tablename__ = "todos"

    todo_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    status: Mapped[Status]

    subtasks: Mapped[list["SubTask"]] = relationship(
        back_populates="todo",
        cascade="delete, delete-orphan",
    )

    @classmethod
    def stmt_get_all(cls) -> Select[tuple[Self]]:
        stmt = select(cls).order_by(desc(cls.created_at))
        return stmt

    @classmethod
    async def get_all(
        cls, session: AsyncSession
    ) -> AsyncIterator[Self]:
        stmt = cls.stmt_get_all()
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

    @classmethod
    async def bulk_create(
        cls,
        session: AsyncSession,
        todos: Iterable[BulkCreateParam],
    ) -> list[Self]:
        # https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html#using-insert-update-and-on-conflict-i-e-upsert-to-return-orm-objects
        return [
            records
            for chunk in get_chunk(todos, n=BULK_SIZE_LIMIT)
            for records in await cls._bulk_create(
                session, chunk
            )
        ]

    @classmethod
    async def _bulk_create(
        cls,
        session: AsyncSession,
        todos: Iterable[BulkCreateParam],
    ) -> list[Self]:
        new_todo_dict = [
            {
                "todo_id": uuid4(),
                "title": todo["title"],
                "status": todo["status"],
            }
            for todo in todos
        ]
        stmt = (
            insert(cls)
            .values(new_todo_dict)
            .options(noload(cls.subtasks))
            .returning(cls)
        )
        return [
            todo
            for todo in (
                (await session.execute(stmt)).scalars()
            )
        ]
