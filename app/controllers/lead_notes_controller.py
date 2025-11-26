from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import role_required
from app.crud.lead_free_note import create_free_note
from app.database import get_db
from app.models.lead import Lead
from app.models.lead_free_notes import LeadFreeNotes
from app.models.user import User
from app.schemas.lead_free_notes import (
    LeadFreeNoteCreate,
    LeadFreeNoteItem,
    LeadFreeNotesResponse,
)


router = APIRouter(prefix="/lead-notes", tags=["Lead Notes"])


@router.post(
    "/add-notes", response_model=dict, dependencies=[Depends(role_required(["Admin"]))]
)
async def assign_sector_city(data: LeadFreeNoteCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    create_free_note(db, data)

    return {"message": "Note added successfully"}


@router.get(
    "/{lead_id}/notes",
    response_model=LeadFreeNotesResponse,
    dependencies=[Depends(role_required(["Admin", "Technician", "User"]))],
)
def get_lead_notes(lead_id: int, db: Session = Depends(get_db)):
    lead_note = db.query(LeadFreeNotes).filter(LeadFreeNotes.lead_id == lead_id).order_by(LeadFreeNotes.created_at.desc()).all()
    if not lead_note:
        raise HTTPException(status_code=404, detail="No notes found for this lead")

    lead_notes: List[LeadFreeNoteItem] = [
        LeadFreeNoteItem.model_validate(note) for note in lead_note
    ]

    return {"lead_id": lead_id, "free_notes": lead_notes}
