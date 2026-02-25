from pydantic import BaseModel, EmailStr
from typing import Optional

class TrafficLeadCreate(BaseModel):
    sector: str
    city: str
    business_name: Optional[str] = None
    contact_person_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    summary: Optional[str] = None