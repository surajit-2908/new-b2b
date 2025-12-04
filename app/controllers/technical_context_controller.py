from app.schemas.message_response import MessageResponse
from fastapi import APIRouter, HTTPException, Depends
from app.models.deal import Deal
from app.schemas.technical_context import TechnicalContextCreate, TechnicalContextOut
from app.models.technical_context import TechnicalContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import role_required

router = APIRouter(prefix="/technical_context", tags=["Technical Context"])


@router.post(
    "/save",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "User"]))],
)
def create_or_update_technical_context(data: TechnicalContextCreate, db: Session = Depends(get_db)):
    """
    Create or update technical context for a deal.
    """
    deal =  db.query(Deal).filter(Deal.id == data.deal_id).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    tech_context = (
        db.query(TechnicalContext)
        .filter(TechnicalContext.deal_id == data.deal_id)
        .first()
    )

    if tech_context:
        # Update existing record
        tech_context.client_main_systems = data.client_main_systems
        tech_context.integration_targets = data.integration_targets
        tech_context.tools_in_scope = data.tools_in_scope
        tech_context.access_required_list = data.access_required_list
        tech_context.credential_provision_method = data.credential_provision_method
        db.commit()
        db.refresh(tech_context)

        return {"message": "Technical context updated successfully"}
        
    else:
        # Create new record
        tech_context = TechnicalContext(
            deal_id=data.deal_id,
            client_main_systems=data.client_main_systems,
            integration_targets=data.integration_targets,
            tools_in_scope=data.tools_in_scope,
            access_required_list=data.access_required_list,
            credential_provision_method=data.credential_provision_method,
        )
        db.add(tech_context)
        db.commit()
        db.refresh(tech_context)
        return {"message": "Technical context saved successfully"}


@router.get("/{deal_id}", response_model=TechnicalContextOut | MessageResponse)
def get_deal_by_lead(deal_id: int, db: Session = Depends(get_db)):
    """
    Retrieve Technical Context by deal ID."""
    technical_context = db.query(TechnicalContext).filter(TechnicalContext.deal_id == deal_id).first()
    if not technical_context:
        return {"message": "No technical context found for this deal"}

    return technical_context
    