from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, role_required
from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.schemas.organic_lead import OrganicLeadCreate, OrganicLeadResponse

router = APIRouter(prefix="/organic-lead", tags=["Organic Leads"])


@router.post(
    "/add-organic-lead",
    response_model=dict,
    dependencies=[Depends(role_required(["Sales"]))],
)
async def add_organic_lead(
    data: OrganicLeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # UPDATE flow
    if data.id is not None:
        existing_lead = db.query(Lead).filter(Lead.id == data.id).first()
        if not existing_lead:
            raise HTTPException(
                status_code=400, detail="Invalid organic lead ID provided."
            )

        # Ensure the lead belongs to the current user
        if existing_lead.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to update this lead."
            )

        existing_lead.sector = data.sector
        existing_lead.city = data.city
        existing_lead.phone = data.phone
        existing_lead.email = data.email
        existing_lead.address = data.address
        existing_lead.summary = data.summary

        db.commit()
        db.refresh(existing_lead)
        return {"message": "Organic lead updated successfully"}

    # CREATE flow
    new_lead = Lead(
        sector=data.sector,
        city=data.city,
        phone=data.phone,
        email=data.email,
        address=data.address,
        summary=data.summary,
        lead_status="Qualified Lead",
        lead_type="Organic Lead",
        user_id=current_user.id,
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {"message": "Organic lead added successfully", "lead_id": new_lead.id}


@router.get(
    "/get-organic-lead/{lead_id}",
    response_model=OrganicLeadResponse,
    dependencies=[Depends(role_required(["Sales"]))],
)
def get_organic_lead_by_id(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.lead_type == "Organic Lead",
            Lead.user_id
            == current_user.id,  # Ensure user can only access their own leads
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404, detail="Organic lead not found or access denied"
        )

    return lead
