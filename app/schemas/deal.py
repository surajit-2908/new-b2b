from pydantic import BaseModel, EmailStr
from datetime import datetime

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
    salesperson_name: str

    deal_close_date: datetime
    
    # 1.2 Commercial Terms (Contract Basics)
    expected_start_date: datetime | None = None
    expected_end_date_or_deadline: datetime | None = None
    client_approved_scope_summary: str
    
    # 1.3 Legal / Framework
    special_terms: str | None = None

    status: str | None = "draft"        # draft / active
    draft_version: int | None = None