from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_city_sector import UserCitySector
from app.models.lead import Lead
from app.schemas.lead import LeadOut
from app.models.user import User
from app.schemas.user_city_sector_schema import UserCitySectorCreate, UserCitySectorOut
from app.auth import role_required

router = APIRouter(prefix="/assign-user", tags=["User Sector Assignment"])

@router.post("/", response_model=UserCitySectorOut, dependencies=[Depends(role_required(["Admin"]))])
def assign_sector_city(data: UserCitySectorCreate, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure unique sector-city assignment
    existing = db.query(UserCitySector).filter(
        UserCitySector.sector == data.sector,
        UserCitySector.city == data.city
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This sector and city combination is already assigned to another user."
        )

    new_assignment = UserCitySector(
        sector=data.sector,
        city=data.city,
        user_id=data.user_id
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

@router.get("/leads", response_model=dict, dependencies=[Depends(role_required(["Admin", "User"]))])
def get_user_assigned_leads(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Optional user ID to filter assigned leads"),
    is_followup: Optional[bool] = Query(False, description="If true, return only follow-up leads"),
    sector: Optional[str] = Query(None, description="Filter leads by sector"),
    city: Optional[str] = Query(None, description="Filter leads by city"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of leads per page")
):
    query = db.query(Lead)

    # ✅ Filter by user assignments if user_id provided
    if user_id:
        assignments = db.query(UserCitySector).filter(UserCitySector.user_id == user_id).all()
        if not assignments:
            return {"data": [], "meta": {"total": 0, "page": page, "limit": limit, "pages": 0}}

        sector_city_pairs = [(a.sector, a.city) for a in assignments]
        conditions = [((Lead.sector == s) & (Lead.city == c)) for s, c in sector_city_pairs]
        if conditions:
            query = query.filter(or_(*conditions))

    if is_followup:
        query = query.filter(Lead.follow_up_status == "Active")

    # ✅ Filter by sector and/or city if provided
    if sector:
        query = query.filter(Lead.sector.ilike(f"%{sector}%"))
    if city:
        query = query.filter(Lead.city.ilike(f"%{city}%"))

    # ✅ Pagination logic
    total = query.count()
    leads = query.order_by(Lead.created_at.desc()) \
                 .offset((page - 1) * limit) \
                 .limit(limit) \
                 .all()
    serialized_leads = [LeadOut.from_orm(lead) for lead in leads]

    return {
        "data": serialized_leads,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "is_followup": is_followup,
            "user_id": user_id,
            "sector": sector,
            "city": city
        }
    }
    
ALLOWED_STATUSES = ["Positive lead", "Not interested"]
@router.put("/lead/{lead_id}/status", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
def update_lead_status(
    lead_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    if status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values are: {', '.join(ALLOWED_STATUSES)}"
        )

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields
    lead.lead_status = status
    if status == "Positive lead":
        lead.follow_up_status = "Active"
    else:
        lead.follow_up_status = "Inactive"

    db.commit()
    db.refresh(lead)

    return {
        "message": "Lead status updated successfully",
        "lead_id": lead.id,
        "status": lead.lead_status,
        "follow_up_status": lead.follow_up_status
    }