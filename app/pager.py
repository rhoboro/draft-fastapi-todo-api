from typing import (
    Callable,
    Self,
    TypeVar,
)

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, noload
from sqlalchemy.sql import Select


class LimitOffset(BaseModel):
    limit: int = Field(ge=0, description="0なら最後まで取得")
    offset: int = Field(
        ge=0, description="データ取得の開始位置"
    )


U = TypeVar("U", bound=DeclarativeBase)


class _PagingInfo(BaseModel):
    count: int
    previous: int | None = None
    next: int | None = None


class Pager[T: BaseModel](BaseModel):
    items: list[T] = Field(
        description="ページング対象のデータ"
    )
    count: int = Field(description="総レコード数")
    previous: int | None = Field(
        description="前のlimit件を取得する場合のoffset"
    )
    next: int | None = Field(
        description="次のlimit件を取得する場合のoffset"
    )

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        query: Select[tuple[U]],
        limit_offset: LimitOffset,
        transformer: Callable[[list[U]], list[T]],
    ) -> Self:
        items, paging = await _paginate(
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


async def _paginate(
    session: AsyncSession,
    query: Select[tuple[U]],
    offset: int,
    limit: int,
) -> tuple[list[U], _PagingInfo]:
    # 渡されたoffsetとlimitを使ってSQL文を実行
    items = await _fetch_items(session, query, offset, limit)
    # 総レコード数を取得
    count = await _get_count(session, query)
    if not count:
        return items, _PagingInfo(count=count)

    if not limit:
        # 最後まで取得済み
        if offset:
            return items, _PagingInfo(count=count, previous=0)
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


async def _fetch_items(
    session: AsyncSession,
    query: Select[tuple[U]],
    offset: int,
    limit: int,
) -> list[U]:
    stmt = query
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    # joinedload の可能性もあるため unique() を呼ぶ
    items = (await session.execute(stmt)).unique().scalars()
    return list(items)


async def _get_count(
    session: AsyncSession,
    query: Select[tuple[U]],
) -> int:
    sub = query.options(noload("*")).order_by(None).subquery()
    stmt = select(func.count()).select_from(sub)
    count = (await session.execute(stmt)).scalar_one()
    return count
