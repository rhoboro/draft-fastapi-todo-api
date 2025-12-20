from uuid import UUID

from app import db
from app.database import AsyncSession
from app.exceptions import NotFound
from app.models import Operation


class GetOperation:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def execute(self, operation_id: UUID) -> Operation:
        async with self.session() as session:
            operation = await db.Operation.get_by_id(
                session, operation_id
            )
            if not operation:
                raise NotFound("Operation", operation_id)
            return Operation.model_validate(operation)
