from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class APIHealthBase(BaseModel):
    datetime: datetime
    message: str = Field(max_length=120)


class BaseUser(BaseModel):
    email: EmailStr = Field(max_length=120)


class UserCreate(BaseUser):
    password: str = Field(min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str