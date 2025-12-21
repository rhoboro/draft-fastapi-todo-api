from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends, Request
from httpx import AsyncClient, HTTPError
from structlog.types import FilteringBoundLogger

from app.models import OperationStatus


class Client:
    def __init__(self, ac: AsyncClient) -> None:
        self.ac = ac

    async def send(
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


async def webhook_client(request: Request) -> Client:
    ac = cast(AsyncClient, request.state.webhook_client)
    return Client(ac=ac)


WebhookClient = Annotated[Client, Depends(webhook_client)]
