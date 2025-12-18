from enum import IntEnum, StrEnum


class Status(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class OperationType(IntEnum):
    IMPORT_TODOS = 1


class OperationStatus(IntEnum):
    NEW = 0
    STARTED = 1
    COMPLETED = 2
    ERROR = -1
