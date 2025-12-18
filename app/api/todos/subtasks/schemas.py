from app.models import BaseModel, Status, SubTask


class ListSubTasksResponse(BaseModel):
    subtasks: list[SubTask]


class CreateSubTaskRequest(BaseModel):
    title: str


class CreateSubTaskResponse(SubTask):
    pass


class GetSubTaskResponse(SubTask):
    pass


class UpdateSubTaskRequest(BaseModel):
    title: str
    status: Status


class UpdateSubTaskResponse(SubTask):
    pass
