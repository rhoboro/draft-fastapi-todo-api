from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api_route import LoggingRoute
from app.exceptions import init_exception_handler
from app.log import init_log
from app.middlewares import init_middlewares

from .api import router as api_router

app = FastAPI(title="fastapi-todo-api")
app.router.route_class = LoggingRoute

init_log()
init_exception_handler(app)
init_middlewares(app)

app.include_router(api_router)


# APIドキュメントには含めない
@app.get("/", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"message": "It worked!!"})
