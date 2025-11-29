import json
from collections.abc import Callable, Coroutine
from typing import Any

import structlog
from fastapi import Request, Response
from fastapi.routing import APIRoute


class LoggingRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def custom_route_handler(
            request: Request,
        ) -> Response:
            await dump_request(request)
            response = await original(request)
            await dump_response(response)

            return response

        return custom_route_handler


async def dump_request(request: Request) -> None:
    try:
        req = json.loads((await request.body()).decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        req = "{}"

    logger = structlog.getLogger()
    logger.info("request", body=req)


async def dump_response(response: Response) -> None:
    try:
        res = json.loads(
            response.body.decode()  # type: ignore
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        res = "{}"

    logger = structlog.getLogger()
    status_code = response.status_code
    logger.info("response", body=res, status_code=status_code)
