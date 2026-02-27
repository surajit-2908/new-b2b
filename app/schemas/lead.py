from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut
from typing import List

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
    
    assigned_technician: Optional[UserOut] = None

    triple_positive_timestamp: Optional[datetime]
    assigned_datetime: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    deal_close_date: Optional[str] = ""
    assigned_user: Optional[UserOut] = None

    model_config = ConfigDict(
        from_attributes=True,
    )
    
class AssignLeadRequest(BaseModel):
    lead_ids: List[int]   # supports single or bulk
    user_id: int