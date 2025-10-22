from pydantic import BaseModel
from typing import Optional

class CityOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True
