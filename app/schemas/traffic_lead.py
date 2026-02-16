from pydantic import BaseModel
from typing import Optional

class TrafficLeadCreate(BaseModel):
    sector: str
    city: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    summary: Optional[str] = None