from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, role_required
from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.models.deal import Deal
from app.schemas.organic_lead import OrganicLeadCreate, OrganicLeadResponse

router = APIRouter(prefix="/organic-lead", tags=["Organic Leads"])


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user, role_required
from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.schemas.organic_lead import OrganicLeadResponse
from app.utils.pagination import paginate
from app.constants.lead_status import ALLOWED_STATUSES

router = APIRouter(prefix="/organic-lead", tags=["Organic Leads"])


@router.get(
    "/list",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "Sales"]))],
)
def list_organic_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: Optional[int] = Query(None, description="Filter by user ID (Admin only)"),

    sector: Optional[str] = Query(None, description="Filter by sector"),
    city: Optional[str] = Query(None, description="Filter by city"),
    status: Optional[str] = Query(None, description="Filter by lead status"),

    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = (
        db.query(Lead, Deal.deal_close_date)
        .outerjoin(Deal, Deal.lead_id == Lead.id)
        ).filter(
            Lead.lead_type == "Organic Lead"
        )
    
    # USER-BASED FILTERING ONLY FOR ADMINS
    if user_id and "Admin" in current_user.role:
        query = query.filter(Lead.user_id == user_id)
    # 🔐 ROLE-BASED VISIBILITY
    elif "Sales" in current_user.role and "Admin" not in current_user.role:
        query = query.filter(Lead.user_id == current_user.id)

    # 🔎 Filters
    if sector:
        query = query.filter(Lead.sector.ilike(f"%{sector}%"))

    if city:
        query = query.filter(Lead.city.ilike(f"%{city}%"))

    if status:
        if status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed values are: {', '.join(ALLOWED_STATUSES)}",
            )
        query = query.filter(Lead.lead_status == status)

    # 📄 Pagination
    leads, meta = paginate(
        query.order_by(Lead.created_at.desc()),
        page,
        limit
    )
    
    serialized_leads = [
        {
            **OrganicLeadResponse.from_orm(lead).dict(),
            "deal_close_date": deal_close_date or ""
        }
        for lead, deal_close_date in leads
    ]

    return {
        "data": serialized_leads,
        "meta": {
            **meta,
            "sector": sector,
            "city": city,
            "status": status,
        },
    }


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
        existing_lead.business_name = data.business_name
        existing_lead.contact_person_name = data.contact_person_name

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
        lead_status="Qualified Lead", # Default status for new leads
        lead_type="Organic Lead",
        user_id=current_user.id,
        business_name=data.business_name,
        contact_person_name=data.contact_person_name
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
