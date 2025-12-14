from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api_route import LoggingRoute
from app.context import bind_todo_id

from .schemas import (
    CreateTodoRequest,
    CreateTodoResponse,
    GetTodoResponse,
    ListTodosResponse,
    UpdateTodoRequest,
    UpdateTodoResponse,
)
from .subtasks import router as subtask_router
from .use_cases import (
    CreateTodo,
    DeleteTodo,
    GetTodo,
    ListTodos,
    UpdateTodo,
)

router = APIRouter(
    tags=["todos"],
    route_class=LoggingRoute,
)


@router.get("", summary="Todoの一覧を取得する")
async def list_todos(
    use_case: ListTodos = Depends(ListTodos),
) -> ListTodosResponse:
    return ListTodosResponse(
        todos=[todo for todo in await use_case.execute()]
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


router.include_router(
    subtask_router,
    prefix="/{todo_id}/subtasks",
    dependencies=[Depends(bind_todo_id)],
)
