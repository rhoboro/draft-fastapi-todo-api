from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings

async_engine = create_async_engine(
    str(settings.DB_URI),
    pool_size=10,
    max_overflow=5,
    pool_timeout=5,
    pool_use_lifo=True,
    pool_pre_ping=True,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)
