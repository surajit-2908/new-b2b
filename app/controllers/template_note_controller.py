from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import Lead
from app.auth import role_required

from app.schemas.template_note import DealCreate
from app.models.deal import Deal

router = APIRouter(prefix="/template-notes", tags=["Template Notes"])


@router.post(
    "/deal",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "User"]))],
)
def create_or_update_deal(data: DealCreate, db: Session = Depends(get_db)):
    
    # Validate Lead
    lead = (
        db.query(Lead)
        .filter(Lead.id == data.lead_id)
        .filter(Lead.lead_status.notin_(["Not interested", "Triple Positive"]))
        .first()
    )
    if not lead:
        raise HTTPException(
            status_code=404, 
            detail="Lead not found or not eligible for this action"
        )

    # Check existing deal
    existing_deal = db.query(Deal).filter(Deal.lead_id == data.lead_id).first()

    if existing_deal:
        # -------- UPDATE EXISTING DEAL --------
        existing_deal.client_name = data.client_name
        existing_deal.primary_contact_name = data.primary_contact_name
        existing_deal.primary_contact_email = data.primary_contact_email
        existing_deal.primary_contact_phone = data.primary_contact_phone
        existing_deal.industry = data.industry
        existing_deal.sector_package = data.sector_package
        existing_deal.deal_name = data.deal_name
        existing_deal.salesperson_name = data.salesperson_name
        existing_deal.deal_close_date = data.deal_close_date
        existing_deal.expected_start_date = data.expected_start_date
        existing_deal.expected_end_date_or_deadline = data.expected_end_date_or_deadline
        existing_deal.client_approved_scope_summary = data.client_approved_scope_summary
        existing_deal.special_terms = data.special_terms
        existing_deal.status = data.status
        existing_deal.draft_version = data.draft_version

        db.commit()
        db.refresh(existing_deal)

        return {"message": "Deal updated successfully"}

    else:
        # -------- CREATE NEW DEAL --------
        new_deal = Deal(
            lead_id=data.lead_id,
            client_name=data.client_name,
            primary_contact_name=data.primary_contact_name,
            primary_contact_email=data.primary_contact_email,
            primary_contact_phone=data.primary_contact_phone,
            industry=data.industry,
            sector_package=data.sector_package,
            deal_name=data.deal_name,
            salesperson_name=data.salesperson_name,
            deal_close_date=data.deal_close_date,
            expected_start_date=data.expected_start_date,
            expected_end_date_or_deadline=data.expected_end_date_or_deadline,
            client_approved_scope_summary=data.client_approved_scope_summary,
            special_terms=data.special_terms,
            status=data.status,
            draft_version=data.draft_version,
        )
        db.add(new_deal)
        db.commit()
        db.refresh(new_deal)

        return {"message": "Deal created successfully"}

