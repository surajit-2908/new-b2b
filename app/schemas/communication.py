from datetime import datetime
from pydantic import BaseModel


class CommunicationCreate(BaseModel):
    deal_id: int
    client_project_contact_name: str
    client_project_contact_email: str
    preferred_channel: str | None = None
    update_frequency: str | None = None


class CommunicationOut(CommunicationCreate):
    id: int
    created_at: datetime | None = None


class Config:
    from_attributes = True
