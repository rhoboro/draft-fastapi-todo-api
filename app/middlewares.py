import time
from uuid import uuid4

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.types import (
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send,
)
from structlog.contextvars import (
    bind_contextvars,
    clear_contextvars,
)


class ProcessTimeMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # リクエスト単位でロガーを初期化
        logger = structlog.get_logger()
        clear_contextvars()

        # リクエストの情報をログに追加
        request = Request(scope)
        bind_contextvars(
            request_id=str(uuid4()),
            path=str(request.url.path),
            method=request.method,
        )

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                # レスポンスから取得した情報をログに追加
                status_code = message["status"]
                bind_contextvars(status_code=status_code)
            await send(message)

        # 次の処理を呼び出し、その処理時間を計測
        start_time = time.perf_counter()
        await self.app(scope, receive, send_wrapper)
        process_time = time.perf_counter() - start_time

        # ログを出力
        logger.info(
            "request completed", process_time=process_time
        )


def init_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:8080",
            "http://127.0.0.1",
            "http://127.0.0.1:8080",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(ProcessTimeMiddleware)
