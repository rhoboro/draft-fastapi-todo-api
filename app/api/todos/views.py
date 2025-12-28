from typing import Annotated, cast
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    UploadFile,
    status,
)

from app.api_route import LoggingRoute
from app.context import bind_todo_id
from app.pager import LimitOffset

from .schemas import (
    CreateTodoRequest,
    CreateTodoResponse,
    GetTodoResponse,
    ImportTodosResponse,
    ListTodosResponse,
    UpdateTodoRequest,
    UpdateTodoResponse,
)
from .subtasks import router as subtask_router
from .use_cases import (
    CreateTodo,
    DeleteTodo,
    GetTodo,
    ImportTodos,
    ListTodos,
    UpdateTodo,
)

router = APIRouter(
    tags=["todos"],
    route_class=LoggingRoute,
)


@router.get("", summary="Todoの一覧を取得する")
async def list_todos(
    limit_offset: Annotated[LimitOffset, Query()],
    use_case: ListTodos = Depends(ListTodos),
) -> ListTodosResponse:
    return cast(
        ListTodosResponse,
        await use_case.execute(limit_offset),
    )


@router.post(
    "",
    summary="Todoを作成する",
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    data: CreateTodoRequest,
    use_case: CreateTodo = Depends(CreateTodo),
) -> CreateTodoResponse:
    return cast(
        CreateTodoResponse, await use_case.execute(data.title)
    )


@router.get(
    "/{todo_id}",
    summary="Todoを取得する",
    dependencies=[Depends(bind_todo_id)],
)
async def get_todo(
    todo_id: UUID,
    use_case: GetTodo = Depends(GetTodo),
) -> GetTodoResponse:
    return cast(
        GetTodoResponse,
        await use_case.execute(todo_id=todo_id),
    )


@router.put(
    "/{todo_id}",
    summary="Todoを更新する",
    dependencies=[Depends(bind_todo_id)],
)
async def update_todo(
    todo_id: UUID,
    data: UpdateTodoRequest,
    use_case: UpdateTodo = Depends(UpdateTodo),
) -> UpdateTodoResponse:
    return cast(
        UpdateTodoResponse,
        await use_case.execute(
            todo_id=todo_id,
            title=data.title,
            status=data.status,
        ),
    )


@router.delete(
    "/{todo_id}",
    summary="Todoを削除する",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(bind_todo_id)],
)
async def delete_todo(
    todo_id: UUID,
    use_case: DeleteTodo = Depends(DeleteTodo),
) -> None:
    await use_case.execute(todo_id=todo_id)


@router.post(
    "/import",
    summary="CSVファイルからTodoを一括インポートする",
)
async def import_todos(
    file: UploadFile,
    use_case: ImportTodos = Depends(ImportTodos),
) -> ImportTodosResponse:
    return ImportTodosResponse(
        operation_id=await use_case.execute(file)
    )


router.include_router(
    subtask_router,
    prefix="/{todo_id}/subtasks",
    dependencies=[Depends(bind_todo_id)],
)
