from pydantic import BaseModel, Field
from datetime import datetime


class LeadFreeNoteBase(BaseModel):
    notes: str | None = Field(None, min_length=5) # min length is added here for notes
    lead_id: int
    
class LeadFreeNoteCreate(LeadFreeNoteBase):
    created_by: int
    
class LeadFreeNoteUpdate(BaseModel):
    notes: str | None = None    
    

    class Config:
        orm_mode = True    