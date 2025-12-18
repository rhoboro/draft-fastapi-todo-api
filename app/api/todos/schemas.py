from uuid import UUID

from app.models import BaseModel, Status, Todo


class ListTodosResponse(BaseModel):
    todos: list[Todo]


class CreateTodoRequest(BaseModel):
    title: str


class CreateTodoResponse(Todo):
    pass


class GetTodoResponse(Todo):
    pass


class UpdateTodoRequest(BaseModel):
    title: str
    status: Status


class UpdateTodoResponse(Todo):
    pass


class ImportTodosResponse(BaseModel):
    operation_id: UUID
