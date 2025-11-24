from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LeadOut(BaseModel):
    id: int
    sector: str
    city: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    summary: Optional[str] = None
    lead_status: str
    follow_up_status: str
    assigned_technician_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
