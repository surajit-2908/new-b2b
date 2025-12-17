from pydantic import BaseModel, ConfigDict

class SectorOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )
