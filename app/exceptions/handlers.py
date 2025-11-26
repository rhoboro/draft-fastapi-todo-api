from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import AppException


def init_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        req: Request, exc: AppException
    ) -> JSONResponse:
        content: dict[str, Any] = {"message": exc.message}
        if exc.details:
            content["details"] = exc.details
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )
