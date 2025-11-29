from app.models import BaseSchema, Status, SubTask


class ListSubTasksResponse(BaseSchema):
    subtasks: list[SubTask]


class CreateSubTaskRequest(BaseSchema):
    title: str


class CreateSubTaskResponse(SubTask):
    pass


class GetSubTaskResponse(SubTask):
    pass


class UpdateSubTaskRequest(BaseSchema):
    title: str
    status: Status


class UpdateSubTaskResponse(SubTask):
    pass
