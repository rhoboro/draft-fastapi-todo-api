from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api_route import LoggingRoute
from app.context import bind_subtask_id

from .schemas import (
    CreateSubTaskRequest,
    CreateSubTaskResponse,
    GetSubTaskResponse,
    ListSubTasksResponse,
    UpdateSubTaskRequest,
    UpdateSubTaskResponse,
)
from .use_cases import (
    CreateSubTask,
    DeleteSubTask,
    GetSubTask,
    ListSubTasks,
    UpdateSubTask,
)

router = APIRouter(route_class=LoggingRoute)


@router.get("", summary="SubTaskの一覧を取得する")
async def list_subtasks(
    todo_id: UUID,
    use_case: ListSubTasks = Depends(ListSubTasks),
) -> ListSubTasksResponse:
    return ListSubTasksResponse(
        subtasks=[
            st
            for st in await use_case.execute(todo_id=todo_id)
        ]
    )


@router.post(
    "",
    summary="SubTaskを作成する",
    status_code=status.HTTP_201_CREATED,
)
async def create_subtask(
    todo_id: UUID,
    data: CreateSubTaskRequest,
    use_case: CreateSubTask = Depends(CreateSubTask),
) -> CreateSubTaskResponse:
    return cast(
        CreateSubTaskResponse,
        await use_case.execute(
            todo_id=todo_id, title=data.title
        ),
    )


@router.get(
    "/{subtask_id}",
    summary="SubTaskを取得する",
    dependencies=[Depends(bind_subtask_id)],
)
async def get_subtask(
    todo_id: UUID,
    subtask_id: UUID,
    use_case: GetSubTask = Depends(GetSubTask),
) -> GetSubTaskResponse:
    return cast(
        GetSubTaskResponse,
        await use_case.execute(
            todo_id=todo_id, subtask_id=subtask_id
        ),
    )


@router.put(
    "/{subtask_id}",
    summary="SubTaskを更新する",
    dependencies=[Depends(bind_subtask_id)],
)
async def update_subtask(
    todo_id: UUID,
    subtask_id: UUID,
    data: UpdateSubTaskRequest,
    use_case: UpdateSubTask = Depends(UpdateSubTask),
) -> UpdateSubTaskResponse:
    return cast(
        UpdateSubTaskResponse,
        await use_case.execute(
            todo_id=todo_id,
            subtask_id=subtask_id,
            title=data.title,
            status=data.status,
        ),
    )


@router.delete(
    "/{subtask_id}",
    summary="SubTaskを削除する",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(bind_subtask_id)],
)
async def delete_subtask(
    todo_id: UUID,
    subtask_id: UUID,
    use_case: DeleteSubTask = Depends(DeleteSubTask),
) -> None:
    return await use_case.execute(
        todo_id=todo_id, subtask_id=subtask_id
    )
