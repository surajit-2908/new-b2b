from pydantic import BaseModel

class SectorOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
