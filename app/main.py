import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from structlog.contextvars import bind_contextvars

from app.exceptions import init_exception_handler
from app.log import init_log
from app.middlewares import init_middlewares

app = FastAPI(title="fastapi-todo-api")

init_log()
init_exception_handler(app)
init_middlewares(app)


# APIドキュメントには含めない
@app.get("/", include_in_schema=False)
async def health() -> JSONResponse:
    bind_contextvars(new_key="new_value")
    logger = structlog.getLogger()
    logger.info("Hello!!")
    return JSONResponse({"message": "It worked!!"})
