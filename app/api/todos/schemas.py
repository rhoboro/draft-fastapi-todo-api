from app.models import BaseSchema, Status, Todo


class ListTodosResponse(BaseSchema):
    todos: list[Todo]


class CreateTodoRequest(BaseSchema):
    title: str


class CreateTodoResponse(Todo):
    pass


class GetTodoResponse(Todo):
    pass


class UpdateTodoRequest(BaseSchema):
    title: str
    status: Status


class UpdateTodoResponse(Todo):
    pass
