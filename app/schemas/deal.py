from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from app.schemas.sector_package import SectorPackageResponse

class DealCreate(BaseModel):
    lead_id: int

    # 1.1 Basic Client & Deal Info
    client_name: str
    primary_contact_name: str
    primary_contact_email: EmailStr
    primary_contact_phone: str | None = None

    industry: str | None = None

    sector_package_id: int
    custom_sector_package: str | None = None
    deal_name: str
    salesperson_name: str | None = None 

    deal_close_date: datetime | None = None 
    
    # 1.2 Commercial Terms (Contract Basics)
    expected_start_date: datetime | None = None
    expected_end_date_or_deadline: datetime | None = None
    client_approved_scope_summary: str
    
    # 1.3 Legal / Framework
    special_terms: str | None = None

    status: str | None = "draft"        # draft / active
    draft_version: int | None = None
        
class DealOut(BaseModel):
    id: int
    lead_id: int
    client_name: str
    primary_contact_name: str | None
    primary_contact_email: str | None
    primary_contact_phone: str | None
    industry: str | None

    sector_package: SectorPackageResponse | None
    custom_sector_package: str | None

    deal_name: str
    salesperson_name: str | None
    deal_close_date: datetime | None

    expected_start_date: datetime | None
    expected_end_date_or_deadline: datetime | None

    client_approved_scope_summary: str | None
    special_terms: str | None

    status: str
    draft_version: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )


