from datetime import datetime
from typing import Annotated

from pydantic import BaseModel as _BaseModel
from pydantic import BeforeValidator, ConfigDict

from app.utils.datetime import to_utc

UTCDatetime = Annotated[datetime, BeforeValidator(to_utc)]


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
