from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session

from app.auth import role_required
from app.crud.lead_free_note import create_free_note
from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.schemas.lead_free_notes import LeadFreeNoteCreate



router = APIRouter(prefix="/lead-notes", tags=["Lead Notes"])

@router.post("/add-notes", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
async def assign_sector_city(data: LeadFreeNoteCreate, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == data.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    create_free_note(db, data)

    return {
        "message": "Note added successfully"
    }
