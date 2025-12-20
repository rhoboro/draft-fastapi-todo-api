from pydantic import field_serializer

from app.models import (
    Operation,
    OperationStatus,
    OperationType,
)


class GetOperationResponse(Operation):
    @field_serializer("status")
    def status_to_name(self, status: OperationStatus) -> str:
        return status.name

    @field_serializer("operation_type")
    def op_type_to_name(
        self, operation_type: OperationType
    ) -> str:
        return operation_type.name
