from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api_route import LoggingRoute

from .schemas import GetOperationResponse
from .use_cases import GetOperation

router = APIRouter(
    tags=["operations"],
    route_class=LoggingRoute,
)


@router.get(
    "/{operation_id}",
    summary="Operationを取得する",
)
async def get_operation(
    operation_id: UUID,
    use_case: Annotated[GetOperation, Depends(GetOperation)],
) -> GetOperationResponse:
    return cast(
        GetOperationResponse,
        await use_case.execute(operation_id=operation_id),
    )
