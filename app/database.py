from typing import Annotated, AsyncIterator

import structlog
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession as _AsyncSession,
)
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.exceptions import AppException
from app.settings import settings

async_engine = create_async_engine(
    str(settings.DB_URI),
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[
    async_sessionmaker[_AsyncSession]
]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as e:
        # DB 関連のエラーはログを残して 500 を返す
        structlog.getLogger().exception(f"{e!r}")
        raise AppException() from e


AsyncSession = Annotated[
    async_sessionmaker[_AsyncSession], Depends(get_session)
]
