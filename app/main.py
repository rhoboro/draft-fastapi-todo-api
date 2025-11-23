from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="fastapi-todo-api")


# APIドキュメントには含めない
@app.get("/", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"message": "It worked!!"})
