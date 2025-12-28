from uuid import UUID

from pydantic import Field

from app.models import BaseModel, Status, Todo
from app.pager import Pager


class ListTodosResponse(Pager[Todo]):
    items: list[Todo] = Field(serialization_alias="todos")


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
