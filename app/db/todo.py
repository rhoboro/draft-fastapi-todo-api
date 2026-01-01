from collections.abc import AsyncIterator, Iterable
from typing import Self, TypedDict
from uuid import UUID, uuid4

from sqlalchemy import Select, desc, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
    selectinload,
)

from app.models import Status
from app.utils import get_chunk

from .base import Base, str_256
from .subtask import SubTask


class BulkTodoCreateParam(TypedDict):
    title: str
    status: Status


BULK_SIZE_LIMIT = 100


class Todo(Base):
    __tablename__ = "todos"

    todo_id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    status: Mapped[Status]

    subtasks: Mapped[list[SubTask]] = relationship(
        back_populates="todo",
        cascade="delete, delete-orphan",
    )

    subtask_count: Mapped[int] = column_property(
        select(func.count(SubTask.subtask_id))
        .where(SubTask.todo_id == todo_id)
        .scalar_subquery()
    )

    @classmethod
    def stmt_get_all(
        cls,
        min_subtasks: int,
        include_subtasks: bool,
    ) -> Select[tuple[Self]]:
        stmt = select(cls)
        if min_subtasks:
            stmt = stmt.where(
                cls.subtask_count >= min_subtasks
            )
        if include_subtasks:
            stmt = stmt.options(selectinload(cls.subtasks))
        stmt = stmt.order_by(desc(cls.created_at))
        return stmt

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        min_subtasks: int,
        include_subtasks: bool,
    ) -> AsyncIterator[Self]:
        stmt = cls.stmt_get_all(
            min_subtasks=min_subtasks,
            include_subtasks=include_subtasks,
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
        await session.refresh(todo)
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
        todos: Iterable[BulkTodoCreateParam],
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
        todos: Iterable[BulkTodoCreateParam],
    ) -> list[Self]:
        new_todo_dict = [
            {
                "todo_id": uuid4(),
                "title": todo["title"],
                "status": todo["status"],
            }
            for todo in todos
        ]
        stmt = insert(cls).values(new_todo_dict).returning(cls)
        return [todo for todo in await session.scalars(stmt)]
