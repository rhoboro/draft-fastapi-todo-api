from typing import Self
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models import OperationStatus, OperationType

from .base import Base, str_256


class Operation(Base):
    __tablename__ = "operations"

    operation_id: Mapped[UUID] = mapped_column(
        primary_key=True
    )
    operation_type: Mapped[OperationType]
    status: Mapped[OperationStatus] = mapped_column(
        default=OperationStatus.NEW
    )
    reason: Mapped[str_256] = mapped_column(default="")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        operation_id: UUID,
        operation_type: OperationType,
    ) -> Self:
        op = cls(
            operation_id=operation_id,
            operation_type=operation_type,
        )
        session.add(op)
        await session.flush()
        return op

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        operation_id: UUID,
    ) -> Self | None:
        stmt = select(cls).where(
            cls.operation_id == operation_id
        )
        op = await session.scalar(stmt)
        if not op:
            return None

        return op

    async def update(
        self,
        session: AsyncSession,
        status: OperationStatus,
        reason: str = "",
    ) -> Self:
        self.status = status
        self.reason = reason
        await session.flush()
        return self
