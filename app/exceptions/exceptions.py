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


class FileTooLarge(AppException):
    status_code: int = 400
    message: str = "The file size cannot exceed %s"

    def __init__(self, max_size: str) -> None:
        super().__init__(message=self.message.format(max_size))
