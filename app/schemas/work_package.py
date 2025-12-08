from pydantic import BaseModel
from datetime import datetime


class BaseClass(BaseModel):
    id: int
    name: str
    created_at: datetime


class Config:
    from_attributes = True


class PackageTypeOut(BaseClass):
    pass


class SkillsOut(BaseClass):
    pass


class ToolsOut(BaseClass):
    pass
