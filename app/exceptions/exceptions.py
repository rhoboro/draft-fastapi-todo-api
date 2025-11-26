from typing import Any
from uuid import UUID


class AppException(Exception):
    status_code: int = 500
    message: str = "Internal Server Error"

    def __init__(
        self,
        details: dict[str, Any] | None = None,
        message: str = "",
    ) -> None:
        self.details = details
        if message:
            self.message = message


class NotFound(AppException):
    status_code: int = 404
    message: str = "Not Found"

    def __init__(
        self, resource: str, resource_id: UUID
    ) -> None:
        super().__init__({resource: str(resource_id)})
