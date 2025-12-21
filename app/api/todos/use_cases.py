import csv
from io import TextIOWrapper
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, UploadFile
from structlog import get_logger

from app import db
from app.api.todos.webhook import WebhookClient
from app.database import AsyncSession
from app.exceptions import FileTooLarge, NotFound
from app.models import (
    OperationStatus,
    OperationType,
    Status,
    Todo,
)


class ListTodos:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
    ) -> list[Todo]:
        async with self.session() as session:
            todos = await db.Todo.get_all(session)
            return [
                Todo.model_validate(todo)
                async for todo in todos
            ]


class CreateTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, title: str) -> Todo:
        async with self.session.begin() as session:
            todo = await db.Todo.create(
                session,
                todo_id=uuid4(),
                title=title,
                status=Status.NEW,
            )
            return Todo.model_validate(todo)


class GetTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, todo_id: UUID) -> Todo:
        async with self.session() as session:
            todo = await db.Todo.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)
            return Todo.model_validate(todo)


class UpdateTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
        title: str,
        status: Status,
    ) -> Todo:
        async with self.session.begin() as session:
            todo = await db.Todo.get_by_id(session, todo_id)
            if not todo:
                raise NotFound("Todo", todo_id)
            await todo.update(session, title, status)
            return Todo.model_validate(todo)


class DeleteTodo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(
        self,
        todo_id: UUID,
    ) -> None:
        async with self.session.begin() as session:
            todo = await db.Todo.get_by_id(session, todo_id)
            if not todo:
                return
            await db.Todo.delete(session, todo)


class ImportTodos:
    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(
        self,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
        webhook: WebhookClient,
    ) -> None:
        self.session = session
        self.background_tasks = background_tasks
        self.webhook = webhook
        self.logger = get_logger(__name__)

    async def execute(self, file: UploadFile) -> UUID:
        operation_id = uuid4()
        async with self.session.begin() as session:
            await db.Operation.create(
                session,
                operation_id=operation_id,
                operation_type=OperationType.IMPORT_TODOS,
            )

        self.background_tasks.add_task(
            self._import_operation,
            operation_id=operation_id,
            file=file,
        )
        return operation_id

    async def _import_operation(
        self,
        operation_id: UUID,
        file: UploadFile,
    ) -> None:
        try:
            # 処理の開始
            await self._update_operation(
                operation_id,
                OperationStatus.STARTED,
            )
            # ここでインポート処理
            await self.import_todo(file)
        except Exception as e:
            # エラー発生時
            await self._update_operation(
                operation_id,
                OperationStatus.ERROR,
                reason=str(e),
            )
        else:
            # 正常終了時
            await self._update_operation(
                operation_id,
                OperationStatus.COMPLETED,
            )

    async def _update_operation(
        self,
        operation_id: UUID,
        status: OperationStatus,
        reason: str = "",
    ) -> None:
        async with self.session.begin() as session:
            op = await db.Operation.get_by_id(
                session,
                operation_id=operation_id,
            )
            if not op:
                raise NotFound("Operation", operation_id)

            from_status = op.status
            await op.update(
                session,
                status=status,
                reason=reason,
            )

        await self.webhook.send(
            operation_id,
            from_status=from_status,
            to_status=status,
            logger=self.logger,
        )

    async def import_todo(
        self, file: UploadFile
    ) -> list[db.Todo]:
        # 実際のファイルサイズをチェック
        await file.seek(self.MAX_FILE_SIZE)
        if await file.read(1):
            raise FileTooLarge("5MB")
        await file.seek(0)

        reader = csv.DictReader(
            TextIOWrapper(file.file, encoding="utf-8"),
            fieldnames=["title", "status"],
        )
        # ヘッダーをスキップ
        next(reader)

        async with self.session.begin() as session:
            data = (
                db.BulkCreateParam(
                    title=row["title"],
                    status=Status(row["status"]),
                )
                for row in reader
            )
            return await db.Todo.bulk_create(session, data)
