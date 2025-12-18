from uuid import UUID

from .base import BaseModel, UTCDatetime
from .enums import OperationStatus, OperationType


class Operation(BaseModel):
    operation_id: UUID
    status: OperationStatus
    operation_type: OperationType
    reason: str = ""
    updated_at: UTCDatetime
