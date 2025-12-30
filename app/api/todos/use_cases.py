import csv
from io import TextIOWrapper
from typing import Literal, overload
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
    TodoWithSubTasks,
)
from app.pager import LimitOffset, Pager


class ListTodos:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @overload
    async def execute(
        self,
        limit_offset: LimitOffset,
        min_subtasks: int,
        include_subtasks: Literal[True],
    ) -> Pager[TodoWithSubTasks]: ...

    @overload
    async def execute(
        self,
        limit_offset: LimitOffset,
        min_subtasks: int,
        include_subtasks: Literal[False],
    ) -> Pager[Todo]: ...

    @overload
    async def execute(
        self,
        limit_offset: LimitOffset,
        min_subtasks: int,
        include_subtasks: bool,
    ) -> Pager[Todo | TodoWithSubTasks]: ...

    async def execute(
        self,
        limit_offset: LimitOffset,
        min_subtasks: int,
        include_subtasks: bool,
    ) -> (
        Pager[Todo]
        | Pager[TodoWithSubTasks]
        | Pager[Todo | TodoWithSubTasks]
    ):
        async with self.session() as session:
            query = db.Todo.stmt_get_all(
                min_subtasks,
                include_subtasks,
            )

            def transformer(
                todos: list[db.Todo],
            ) -> list[Todo | TodoWithSubTasks]:
                t = (
                    TodoWithSubTasks
                    if include_subtasks
                    else Todo
                )
                return [
                    t.model_validate(todo) for todo in todos
                ]

            return await Pager.paginate(
                session=session,
                query=query,
                limit_offset=limit_offset,
                transformer=transformer,
            )


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
        # 実ファイルサイズをチェック
        await file.seek(self.MAX_FILE_SIZE)
        if await file.read(1):
            raise FileTooLarge("5MB")
        await file.seek(0)

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
            await self.import_todos(file)
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
            in_background=True,
        )

    async def import_todos(
        self, file: UploadFile
    ) -> tuple[list[db.Todo], list[db.SubTask]]:
        reader = csv.DictReader(
            TextIOWrapper(file.file, encoding="utf-8"),
            fieldnames=[
                "title",
                "status",
                "subtask_title",
                "subtask_status",
            ],
        )
        # ヘッダーをスキップ
        next(reader)

        async with self.session.begin() as session:
            todo_data: list[db.BulkTodoCreateParam] = []
            subtask_rows: list[list[dict[str, str]]] = []
            for row in reader:
                if row["title"]:
                    # CSVファイルのTODO行
                    todo_data.append(
                        db.BulkTodoCreateParam(
                            title=row["title"],
                            status=Status(row["status"]),
                        )
                    )
                    subtask_rows.append([])
                else:
                    # CSVファイルのSubTask行
                    subtask_rows[-1].append(
                        {
                            "title": row["subtask_title"],
                            "status": row["subtask_status"],
                        }
                    )

            # Todoを追加
            new_todos = await db.Todo.bulk_create(
                session, todo_data
            )
            assert len(new_todos) == len(subtask_rows)

            # 作成されたtodo_idを使ってSubTaskを追加
            subtask_data = [
                db.BulkSubTaskCreateParam(
                    todo_id=todo.todo_id,
                    title=subtask["title"],
                    status=Status(subtask["status"]),
                )
                for (todo, subtask_row) in zip(
                    new_todos, subtask_rows
                )
                for subtask in subtask_row
            ]
            new_subtasks = await db.SubTask.bulk_create(
                session, subtask_data
            )
            return new_todos, new_subtasks
