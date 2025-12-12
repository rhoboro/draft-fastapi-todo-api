import os
from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, SessionTransaction

from app.database import async_engine, get_session
from app.main import app
from app.models import Base


@pytest.fixture(scope="session")
def anyio_backend() -> tuple[str, dict[str, bool]]:
    return "asyncio", {"use_uvloop": True}


@pytest.fixture
async def ac() -> AsyncIterator[AsyncClient]:
    headers = {"APP-API-KEY": "DUMMY-KEY"}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://test.invalid",
        headers=headers,
    ) as c:
        yield c


def get_test_db_name() -> tuple[str, str, str]:
    full_uri = os.environ["DB_URI"]
    base_uri, testdb = full_uri.rsplit("/", 1)
    return full_uri, base_uri, testdb


@pytest.fixture(scope="session")
async def setup_test_db() -> AsyncIterator[None]:
    _, base_uri, testdb = get_test_db_name()
    engine = create_async_engine(base_uri)

    # 常に空の状態でデータベースを用意
    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        await conn.execute(
            text(f"DROP DATABASE IF EXISTS {testdb}")
        )
        await conn.execute(text(f"CREATE DATABASE {testdb}"))

    # すべてのテストケースをここで実行
    yield

    # データベースの破棄
    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))
        await conn.execute(text(f"DROP DATABASE {testdb}"))

    # 作成したエンジンの接続を破棄
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_tables(
    setup_test_db: AsyncIterator[None],
) -> AsyncIterator[None]:
    full_uri, _, _ = get_test_db_name()
    engine = create_async_engine(full_uri)

    # Mapped Classの定義からテーブルを作成
    async with engine.begin() as con:
        await con.run_sync(
            lambda con_sync: Base.metadata.create_all(
                con_sync.engine
            )
        )

    # すべてのテストケースをここで実行
    yield
    # アプリケーションからの接続を破棄
    await async_engine.dispose()
    # 作成したエンジンの接続を破棄
    await engine.dispose()


@pytest.fixture
async def test_session() -> AsyncIterator[
    async_sessionmaker[AsyncSession]
]:
    full_uri, _, _ = get_test_db_name()
    engine = create_async_engine(full_uri)
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()

        AsyncSessionLocal = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )

        async_session = AsyncSessionLocal()

        @event.listens_for(
            async_session.sync_session, "after_transaction_end"
        )
        def end_savepoint(
            session: Session, transaction: SessionTransaction
        ) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        async def test_get_session() -> AsyncIterator[
            async_sessionmaker[AsyncSession]
        ]:
            try:
                yield AsyncSessionLocal
            except SQLAlchemyError:
                pass

        app.dependency_overrides[get_session] = (
            test_get_session
        )

        # このSessionオブジェクトは
        # テストデータの作成に利用する
        yield AsyncSessionLocal
        await async_session.close()
        # テストケース実行ごとにロールバック
        await conn.rollback()

    # 作成したエンジンの接続を破棄
    await engine.dispose()
