from sqlalchemy.orm import Session
from app.models.lead_free_note import LeadFreeNote
from app.schemas.lead_free_note import LeadFreeNoteCreate


def create_free_note(db: Session, data: LeadFreeNoteCreate):
        note = LeadFreeNote(
            notes=data.notes,
            lead_id=data.lead_id,
            created_by=data.created_by
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
