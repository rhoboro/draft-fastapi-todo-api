from asyncio import TaskGroup
from collections.abc import AsyncIterator
from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends, Request
from httpx import AsyncClient, HTTPError
from structlog.types import FilteringBoundLogger

from app.models import OperationStatus


class Client:
    def __init__(self, ac: AsyncClient, tg: TaskGroup) -> None:
        self.ac = ac
        self.tg = tg

    async def send(
        self,
        operation_id: UUID,
        from_status: OperationStatus,
        to_status: OperationStatus,
        logger: FilteringBoundLogger,
        in_background: bool = False,
    ) -> None:
        coro = self._send(
            operation_id, from_status, to_status, logger
        )
        if in_background:
            self.tg.create_task(coro)
        else:
            await coro

    async def _send(
        self,
        operation_id: UUID,
        from_status: OperationStatus,
        to_status: OperationStatus,
        logger: FilteringBoundLogger,
    ) -> None:
        try:
            res = await self.ac.post(
                "/import_todo",
                json={
                    "operation_id": str(operation_id),
                    "from": from_status.name,
                    "to": to_status.name,
                },
            )
            res.raise_for_status()

        except HTTPError as e:
            logger.info(
                "webhook error",
                operation_id=str(operation_id),
                from_status=from_status.name,
                to_status=to_status.name,
                error=repr(e),
            )

        else:
            logger.info(
                "webhook success",
                operation_id=str(operation_id),
                from_status=from_status.name,
                to_status=to_status.name,
            )


async def webhook_client(
    request: Request,
) -> AsyncIterator[Client]:
    ac = cast(AsyncClient, request.state.webhook_client)
    async with TaskGroup() as tg:
        yield Client(ac=ac, tg=tg)


WebhookClient = Annotated[Client, Depends(webhook_client)]
