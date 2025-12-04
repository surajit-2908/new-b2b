from pydantic import BaseModel
from datetime import datetime


class TechnicalContextCreate(BaseModel):
    deal_id: int
    client_main_systems: str
    integration_targets: str | None = None
    tools_in_scope: str
    access_required_list: str
    credential_provision_method: str


class TechnicalContextOut(TechnicalContextCreate):
    id: int
    created_at: datetime | None = None


class Config:
    from_attributes = True
