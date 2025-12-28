from collections.abc import Sequence
from typing import (
    Callable,
    Generic,
    Self,
    TypeVar,
)

from fastapi import Query
from pydantic import BaseModel, Field
from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from sqlalchemy.sql import Select

from app.db import Base

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=Base)


class _PagingInfo(BaseModel):
    count: int
    previous: int | None = None
    next: int | None = None


class LimitOffset(BaseModel):
    limit: int = Query(
        0, ge=0, description="0 の場合は最後まで取得"
    )
    offset: int = Query(0, description="データ取得開始位置")


class Pager(BaseModel, Generic[T]):
    items: Sequence[T] = Field(
        description="ページング対象のデータ"
    )
    count: int = Field(description="全件数")
    previous: int | None = Field(
        description="前の limit 件を取得する場合の offset"
    )
    next: int | None = Field(
        description="次の limit 件を取得する場合の offset"
    )

    @classmethod
    async def paginate(
        cls,
        transformer: Callable[[list[U]], list[T]],
        session: AsyncSession,
        query: Select[tuple[U]],
        limit_offset: LimitOffset,
    ) -> Self:
        items, paging = await cls._paginate(
            session,
            query,
            offset=limit_offset.offset,
            limit=limit_offset.limit,
        )
        return cls(
            items=transformer(items),
            count=paging.count,
            previous=paging.previous,
            next=paging.next,
        )

    @classmethod
    async def _paginate(
        cls,
        session: AsyncSession,
        query: Select[tuple[U]],
        offset: int,
        limit: int,
    ) -> tuple[list[U], _PagingInfo]:
        pagination_query = query
        if offset:
            pagination_query = pagination_query.offset(offset)
        if limit:
            pagination_query = pagination_query.limit(limit)
        items = list(
            (await session.execute(pagination_query)).scalars()
        )
        count_query = (
            query.order_by(None)
            .options(noload("*"))
            .subquery()
        )
        count = (
            (
                await session.execute(
                    select(
                        func.count(literal_column("*"))
                    ).select_from(count_query)
                )
            )
            .scalars()
            .one()
        )
        if not count:
            return items, _PagingInfo(count=count)

        if not limit:
            # limit がない場合は最後まで取得しているので
            # previous のみ確認
            if offset:
                return items, _PagingInfo(
                    count=count, previous=0
                )
            else:
                return items, _PagingInfo(count=count)

        next_ = (
            (offset + limit)
            if count > offset + len(items)
            else None
        )
        previous = max(0, offset - limit) if offset else None
        return items, _PagingInfo(
            count=count, previous=previous, next=next_
        )
