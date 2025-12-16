from app.models.communication import Communication
from app.schemas.communication import CommunicationCreate, CommunicationOut
from app.schemas.message_response import DataResponse, MessageResponse
from fastapi import APIRouter, HTTPException, Depends
from app.models.deal import Deal
from app.models.technical_context import TechnicalContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import role_required

router = APIRouter(prefix="/communication", tags=["Communication"])


@router.post(
    "/save",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "User"]))],
)
def create_or_update_communication(data: CommunicationCreate, db: Session = Depends(get_db)):
    """
    Create or update communication for a deal.
    """
    deal =  db.query(Deal).filter(Deal.id == data.deal_id).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    communication = (
        db.query(Communication)
        .filter(Communication.deal_id == data.deal_id)
        .first()
    )

    if communication:
        # Update existing record
        communication.client_project_contact_name = data.client_project_contact_name
        communication.client_project_contact_email = data.client_project_contact_email
        communication.preferred_channel = data.preferred_channel
        communication.update_frequency = data.update_frequency
        db.commit()

        return {"message": "Communication updated successfully"}
        
    else:
        # Create new record
        communication = Communication(
            deal_id=data.deal_id,
            client_project_contact_name=data.client_project_contact_name,
            client_project_contact_email=data.client_project_contact_email,
            preferred_channel=data.preferred_channel,
            update_frequency=data.update_frequency,
        )
        db.add(communication)
        db.commit()
        return {"message": "Communication saved successfully"}


@router.get("/{deal_id}", response_model=DataResponse[CommunicationOut] | MessageResponse)
def get_communication_by_deal(deal_id: int, db: Session = Depends(get_db)):
    """
    Retrieve communication by deal ID."""
    communication = db.query(Communication).filter(Communication.deal_id == deal_id).first()
    if not communication:
        return {"message": "No communication found for this deal"}

    return {"data": communication}
    