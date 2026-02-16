from pydantic import BaseModel, EmailStr
from typing import Optional

class TrafficLeadCreate(BaseModel):
    sector: str
    city: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    summary: Optional[str] = None