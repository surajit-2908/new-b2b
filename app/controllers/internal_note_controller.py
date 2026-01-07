from app.models.internal_note import InternalNote
from app.schemas.internal_note import InternalNoteCreate, InternalNoteOut
from app.schemas.message_response import DataResponse, MessageResponse
from fastapi import APIRouter, HTTPException, Depends
from app.models.deal import Deal
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import role_required

router = APIRouter(prefix="/internal-note", tags=["Internal Note"])


@router.post(
    "/save",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "Sales"]))],
)
def create_or_update_internal_note(data: InternalNoteCreate, db: Session = Depends(get_db)):
    """
    Create or update internal note for a deal.
    """
    deal =  db.query(Deal).filter(Deal.id == data.deal_id).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    internal_note = (
        db.query(InternalNote)
        .filter(InternalNote.deal_id == data.deal_id)
        .first()
    )

    if internal_note:
        # Update existing record
        internal_note.internal_risks_and_warnings = data.internal_risks_and_warnings
        internal_note.internal_margin_sensitivity = data.internal_margin_sensitivity
        internal_note.internal_notes = data.internal_notes
        
        db.commit()

        return {"message": "Internal note updated successfully"}
        
    else:
        # Create new record
        internal_note = InternalNote(
            deal_id=data.deal_id,
            internal_risks_and_warnings=data.internal_risks_and_warnings,
            internal_margin_sensitivity=data.internal_margin_sensitivity,
            internal_notes=data.internal_notes,
        )
        db.add(internal_note)
        db.commit()

        return {"message": "Internal note saved successfully"}


@router.get("/{deal_id}", response_model=DataResponse[InternalNoteOut] | MessageResponse)
def get_internal_note_by_deal(deal_id: int, db: Session = Depends(get_db)):
    """
    Retrieve internal note by deal ID."""
    internal_note = db.query(InternalNote).filter(InternalNote.deal_id == deal_id).first()
    if not internal_note:
        return {"message": "No internal note found for this deal"}

    return {"data": internal_note}
    