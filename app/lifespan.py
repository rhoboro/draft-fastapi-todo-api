from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from httpx import AsyncClient

from app.settings import settings


class State(TypedDict):
    webhook_client: AsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    async with AsyncClient(
        base_url=settings.WEBHOOK_URL
    ) as ac:
        yield State(webhook_client=ac)
