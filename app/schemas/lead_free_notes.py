from typing import List
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class LeadFreeNoteBase(BaseModel):
    notes: str | None = Field(None, min_length=5)  # min length is added here for notes
    lead_id: int


class LeadFreeNoteCreate(LeadFreeNoteBase):
    created_by: int


class LeadFreeNoteUpdate(BaseModel):
    notes: str | None = None


class LeadFreeNoteItem(BaseModel):
    id: int
    notes: str
    created_at: datetime
    updated_at: datetime | None
    created_by_user: UserOut | None
    updated_by_user: UserOut | None

    model_config = {"from_attributes": True}


class LeadFreeNoteResponse(BaseModel):
    lead_id: int
    free_notes: List[LeadFreeNoteItem]
    template_notes: List[str] = []

    class Config:
        orm_mode = True
