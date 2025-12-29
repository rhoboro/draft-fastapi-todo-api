from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    MetaData,
    String,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from app.models.enums import (
    OperationStatus,
    OperationType,
    Status,
)
from app.utils.datetime import utcnow

convention = {
    "pk": "pk_%(table_name)s",
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": (
        "fk_%(table_name)s_%(column_0_name)s"
        "_%(referred_table_name)s"
    ),
}

type str_256 = str
type str_64 = str

type_map = {
    str_64: String(64),
    str_256: String(256),
    datetime: DateTime(timezone=True),
    Status: Enum(Status, native_enum=False),
    OperationStatus: Enum(
        OperationStatus,
        name="operation_status",
    ),
    OperationType: Integer,
}


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    type_annotation_map = type_map

    created_at: Mapped[datetime] = mapped_column(
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow, onupdate=utcnow
    )

    def __repr__(self) -> str:
        columns = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        return f"<{self.__class__.__name__}({columns})>"
