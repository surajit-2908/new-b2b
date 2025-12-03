from pydantic import BaseModel

class SectorPackageResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True 
