from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from datetime import datetime, timezone
from app.models.communication import Communication
from app.models.deal import Deal
from app.models.internal_note import InternalNote
from app.models.technical_context import TechnicalContext
from app.models.user_city_sector import UserCitySector
from app.models.lead import Lead
from app.models.work_package import WorkPackage
from app.schemas.lead import LeadOut, AssignLeadRequest
from app.models.user import User
from app.schemas.user_city_sector_schema import UserCitySectorCreate
from app.auth import role_required
from app.utils.pagination import paginate
from app.constants.lead_status import ALLOWED_STATUSES
from app.schemas.user import UserOut

router = APIRouter(prefix="/sales", tags=["User Sector Assignment"])

@router.post("/city-sector/assign-user", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
def assign_sector_city(data: UserCitySectorCreate, db: Session = Depends(get_db)):
    """
    Assign a sector and city to a user.
    """
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure unique sector-city assignment
    existing = (
        db.query(UserCitySector)
        .filter(UserCitySector.sector == data.sector, UserCitySector.city == data.city)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This sector and city combination is already assigned to another user.",
        )

    new_assignment = UserCitySector(
        sector=data.sector, city=data.city, user_id=data.user_id
    )

    db.add(new_assignment)
    db.commit()

    return {"message": "Sector and City assigned successfully"}


@router.get(
    "/leads",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "Sales"]))],
)
def get_user_assigned_leads(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(
        None, description="Optional user ID to filter assigned leads"
    ),
    is_followup: Optional[bool] = Query(
        False, description="If true, return only follow-up leads"
    ),
    sector: Optional[str] = Query(None, description="Filter leads by sector"),
    city: Optional[str] = Query(None, description="Filter leads by city"),
    status: Optional[str] = Query(None, description="Filter leads by status"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of leads per page"),
    lead_type: Optional[str] = Query(None, description="Filter by lead type (Traffic Lead/Scrapping Lead)"),
    assigned: Optional[bool] = Query(None, description="If true, return only leads that are assigned to a user")
):        
    """
    Get leads assigned to a user based on their sector and city assignments, with optional filters for follow-up status, sector, city, lead status, and lead type. Supports pagination.
    """
    query = (
    db.query(Lead, Deal.deal_close_date, User)
    .outerjoin(Deal, Deal.lead_id == Lead.id)
    .outerjoin(User, User.id == Lead.user_id)
)

    # ✅ Filter by user assignments if user_id provided
    if user_id:
        assignments = (
            db.query(UserCitySector).filter(UserCitySector.user_id == user_id).all()
        )
        if not assignments:
            return {
                "data": [],
                "meta": {"total": 0, "page": page, "limit": limit, "pages": 0},
            }

        sector_city_pairs = [(a.sector, a.city) for a in assignments]
        conditions = [
            ((Lead.sector == s) & (Lead.city == c)) for s, c in sector_city_pairs
        ]
        if conditions:
            query = query.filter(or_(*conditions))

    if is_followup:
        query = query.filter(Lead.follow_up_status == "Active")

    # ✅ Filter by sector and/or city if provided
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
        query = query.filter(Lead.lead_status.ilike(f"%{status}%"))
        
    if lead_type:
        query = query.filter(Lead.lead_type.ilike(f"%{lead_type}%"))
        
    if assigned is not None:
        if assigned:
            query = query.filter(Lead.user_id.isnot(None))
        else:
            query = query.filter(Lead.user_id.is_(None))
        
    # ✅ Pagination logic
    leads, meta = paginate(query.order_by(Lead.created_at.desc()), page, limit)
    serialized_leads = []

    for lead, deal_close_date, user in leads:
        lead_obj = LeadOut.model_validate(lead)
        lead_data = lead_obj.model_dump()

        lead_data["deal_close_date"] = deal_close_date or ""
        lead_data["assigned_user"] = (
            UserOut.model_validate(user).model_dump() if user else None
        )

        serialized_leads.append(lead_data)
    return {
        "data": serialized_leads,
        "meta": {
            "total": meta["total"],
            "page": meta["page"],
            "limit": meta["limit"],
            "pages": meta["pages"],
            "is_followup": is_followup,
            "user_id": user_id,
            "sector": sector,
            "city": city,
        },
    }


@router.put(
    "/lead/{lead_id}/status",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "Sales"]))],
)
def update_lead_status(lead_id: int, status: str, db: Session = Depends(get_db)):
    """
    Update the status of a lead.
    """
    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values are: {', '.join(ALLOWED_STATUSES)}",
        )

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields

    if status == "Qualified Lead":
        lead.follow_up_status = "Active"
    elif status == "Active Lead":
        lead = validate_double_positive(lead)
    elif status == "Fulfillment Stage":
        lead = validate_triple_positive(lead, db)
    else:
        lead.follow_up_status = "Inactive"

    lead.lead_status = status
    db.commit()
    db.refresh(lead)

    if(status == "Fulfillment Stage"):
        deal = db.query(Deal).filter(Deal.lead_id == lead.id).first() # already validated in validate_triple_positive
        db.query(WorkPackage).filter(WorkPackage.deal_id == deal.id).update({"bidding_status": "Active"})
        db.commit()

    return {
        "message": "Lead status updated successfully",
        "lead_id": lead.id,
        "status": lead.lead_status,
        "follow_up_status": lead.follow_up_status,
    }


def validate_double_positive(lead: Lead):
    if lead.lead_status != "Qualified Lead":
        raise HTTPException(
            status_code=400,
            detail="Lead must be 'Qualified Lead' before marking as 'Active Lead'",
        )
    lead.follow_up_status = "Active"
    return lead


def validate_triple_positive(lead: Lead, db: Session):
    if lead.lead_status != "Active Lead":
        raise HTTPException(
            status_code=400,
            detail="Lead must be 'Active Lead' before marking as 'Fulfillment Stage'",
        )

    existing_deal = db.query(Deal).filter(Deal.lead_id == lead.id).first()
    if not existing_deal:
        raise HTTPException(
            status_code=400,
            detail="A deal must be created for this lead before marking as 'Fulfillment Stage'",
        )
    existing_wp = (
        db.query(WorkPackage).filter(WorkPackage.deal_id == existing_deal.id).first()
    )
    existing_technical_context = (
        db.query(TechnicalContext)
        .filter(TechnicalContext.deal_id == existing_deal.id)
        .first()
    )
    existing_communication = (
        db.query(Communication)
        .filter(Communication.deal_id == existing_deal.id)
        .first()
    )
    existing_internal_note = (
        db.query(InternalNote).filter(InternalNote.deal_id == existing_deal.id).first()
    )
    
    if not all(
        [
            existing_wp,
            existing_technical_context,
            existing_communication,
            existing_internal_note,
        ]
    ):
  
        raise HTTPException(
            status_code=400,
            detail="Subcontract, Technical Context, Communication, and Internal Note must be completed for this deal before marking as 'Fulfillment Stage'",
        )
        
    # Get max bidding_duration from all work packages
    max_duration = db.query(func.max(WorkPackage.bidding_duration_days)).filter(
        WorkPackage.deal_id == existing_deal.id
    ).scalar()

    # update deal table
    existing_deal.max_duration = max_duration

    lead.follow_up_status = "Active"
    lead.triple_positive_timestamp = func.now()
    return lead

@router.get("/lead-user/{lead_id}", response_model=UserOut)
def get_user_by_lead(lead_id: int, db: Session = Depends(get_db)):

    # 1️⃣ Fetch Lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    user = None

    # 2️⃣ Organic Lead → direct user_id
    if lead.lead_type == "Organic Lead":
        if not lead.user_id:
            raise HTTPException(status_code=404, detail="User not assigned to this organic lead")

        user = db.query(User).filter(User.id == lead.user_id).first()

    # 3️⃣ Other Leads → lookup from mapping
    else:
        mapping = db.query(UserCitySector).filter(
            UserCitySector.city == lead.city,
            UserCitySector.sector == lead.sector
        ).first()

        if not mapping:
            raise HTTPException(
                status_code=404,
                detail="No user mapping found for this city & sector"
            )

        user = db.query(User).filter(User.id == mapping.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user  

@router.put("/assign-user")
def assign_user_to_leads(
    payload: AssignLeadRequest,
    db: Session = Depends(get_db)
):
    # fetch leads
    leads = db.query(Lead).filter(Lead.id.in_(payload.lead_ids)).all()

    if not leads:
        raise HTTPException(status_code=404, detail="No leads found")

    current_time = datetime.now(timezone.utc)

    # update leads
    for lead in leads:
        lead.user_id = payload.user_id
        lead.assigned_datetime = current_time

    db.commit()

    return {
        "message": f"{len(leads)} lead(s) assigned successfully",
        "lead_ids": [lead.id for lead in leads],
        "assigned_user": payload.user_id,
        "assigned_datetime": current_time
    }