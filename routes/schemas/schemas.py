from datetime import datetime

from pydantic import BaseModel, Field


class APIHealthBase(BaseModel):
    datetime: datetime
    message: str = Field(max_length=120)
