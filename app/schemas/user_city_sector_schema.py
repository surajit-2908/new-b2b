from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(
        from_attributes=True,
    )

class BasicUserCitySectorOut(BaseModel):
    sector: str
    city: str

    model_config = ConfigDict(
        from_attributes=True,
    )
