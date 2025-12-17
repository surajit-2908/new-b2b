from pydantic import BaseModel, ConfigDict
from datetime import datetime


class InternalNoteCreate(BaseModel):
    deal_id: int
    internal_risks_and_warnings: str | None = None
    internal_margin_sensitivity: str
    internal_notes: str | None = None


class InternalNoteOut(InternalNoteCreate):
    id: int
    created_at: datetime | None = None


    model_config = ConfigDict(
        from_attributes=True,
    )
