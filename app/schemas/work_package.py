from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


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


class PackageBase(BaseModel):
    id: Optional[int] = None
    package_title: str
    package_type_id: int
    package_summary: str
    custom_package_type: Optional[str] = None
    key_deliverables: str
    acceptance_criteria: str
    required_skills_ids: List[int]
    primary_tools_ids: List[int]
    package_estimated_complexity: str
    package_price_allocation: Optional[Decimal] = None
    dependencies_ids: List[int]

    class Config:
        from_attributes = True


class WorkPackageCreate(BaseModel):
    deal_id: int
    packages: List[PackageBase]

    class Config:
        from_attributes = True


class PackageBaseOut(BaseModel):
    id: Optional[int] = None
    package_title: str
    package_type: PackageTypeOut
    package_summary: str
    custom_package_type: Optional[str] = None
    key_deliverables: str
    acceptance_criteria: str
    required_skills: List[SkillsOut]
    primary_tools: List[ToolsOut]
    package_estimated_complexity: str
    package_price_allocation: Optional[Decimal] = None
    dependencies: List[BaseClass]

    class Config:
        from_attributes = True


class WorkPackageOut(BaseModel):
    deal_id: int
    packages: List[PackageBaseOut]
