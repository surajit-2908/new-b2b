from pydantic import BaseModel
from datetime import datetime

class UserCitySectorCreate(BaseModel):
    sector: str
    city: str
    user_id: int

class UserCitySectorOut(BaseModel):
    id: int
    sector: str
    city: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
