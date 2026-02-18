from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.schemas.user import UserOut


class BaseClass(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class PackageTypeOut(BaseClass):
    pass


class SkillsOut(BaseClass):
    pass


class ToolsOut(BaseClass):
    pass


class PackageBase(BaseModel):
    id: Optional[int] = None
    package_number: Optional[str] = None
    package_title: str
    package_type_id: int
    package_summary: str
    custom_package_type: Optional[str] = None
    key_deliverables: str
    acceptance_criteria: str
    required_skills_ids: List[int]
    primary_tools_ids: List[int]
    required_tools_ids: List[int]
    package_estimated_complexity: str
    package_price_allocation: Optional[float] = None
    dependencies_ids: List[int]
    bidding_duration_days: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkPackageCreate(BaseModel):
    deal_id: int
    packages: List[PackageBase]

    model_config = ConfigDict(
        from_attributes=True,
    )


class PackageBaseOut(BaseModel):
    id: Optional[int] = None
    package_number: Optional[str] = None
    package_title: str
    package_type: PackageTypeOut
    package_summary: str
    custom_package_type: Optional[str] = None
    key_deliverables: str
    acceptance_criteria: str
    required_skills: List[SkillsOut]
    primary_tools: List[ToolsOut]
    required_tools: List[ToolsOut]
    package_estimated_complexity: str
    package_price_allocation: Optional[float] = None
    dependencies: List[BaseClass]
    bidding_duration_days: int
    bidding_status: Optional[str] = None
    assigned_technician: Optional[UserOut] = None
    user_bidding_placed: Optional[bool] = None
    lowest_bid: Optional[float] = None
    

    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkPackageOut(BaseModel):
    deal_id: int
    packages: List[PackageBaseOut]

class TechnicianPackageOut(BaseModel):
    id: Optional[int] = None
    package_number: Optional[str] = None
    package_title: str
    package_type: PackageTypeOut
    package_price_allocation: Optional[float] = None
    bidding_duration_days: int
    package_estimated_complexity: str
    required_skills: List[SkillsOut]
    lowest_bid: Optional[float] = None
    lead_id: int
    expected_end_date_or_deadline: datetime | None
      
    model_config = ConfigDict(
        from_attributes=True,
    )
    
class AdminPackageOut(BaseModel):
    id: Optional[int] = None
    package_number: Optional[str] = None
    package_title: str
    package_type: PackageTypeOut
    package_price_allocation: Optional[float] = None
    bidding_duration_days: int
    package_estimated_complexity: str
    required_skills: List[SkillsOut]
    lowest_bid: Optional[float] = None
    lead_id: int
      
    model_config = ConfigDict(
        from_attributes=True,
    )

class UpdatedPackagesNames(BaseModel):
    package_number: str
    package_id: int