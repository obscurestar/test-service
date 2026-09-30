from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class NewUserRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=32)
    last_name: str = Field(min_length=1, max_length=32)


class HelloRequest(BaseModel):
    user_id: UUID


class SpyResponse(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    last_access: date
    use_count: int