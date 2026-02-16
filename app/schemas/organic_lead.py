from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut


class OrganicLeadCreate(BaseModel):
    id: Optional[int] = None
    sector: str
    city: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    summary: Optional[str] = None
    
    
    
class OrganicLeadResponse(BaseModel):
    id: int
    sector: str
    city: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    summary: Optional[str] = None
    lead_status: str
    lead_type: str
    created_at: datetime
    deal_close_date: Optional[str] = ""

    
    model_config = ConfigDict(
        from_attributes=True,
    )