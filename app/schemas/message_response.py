from pydantic import BaseModel
from typing import Generic, TypeVar

class MessageResponse(BaseModel):
    message: str

T = TypeVar("T")

class DataResponse(BaseModel, Generic[T]):
    data: T
