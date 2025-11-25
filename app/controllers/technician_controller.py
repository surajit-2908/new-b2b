from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadOut
from app.auth import role_required

from app.models.user import User
from app.auth import get_current_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/technician", tags=["Technician"])


@router.get("/leads", response_model=dict, dependencies=[Depends(role_required(["Technician", "Admin"]))])
def get_unassigned_triple_positive_leads(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Leads per page"),
    sector: str | None = Query(None, description="Filter by business sector"),
    city: str | None = Query(None, description="Filter by city")
):
    """
    List leads where:
    - lead_status = 'Triple Positive'
    - assigned_technician_id IS NULL
    """
    query = db.query(Lead).filter(
        Lead.lead_status == "Triple Positive",
        Lead.assigned_technician_id.is_(None)
    )

    # Apply filters dynamically
    if sector:
        query = query.filter(Lead.sector == sector)
    if city:
        query = query.filter(Lead.city == city)

    leads, meta = paginate(query.order_by(Lead.created_at.desc()), page, limit)

    leads_out: List[LeadOut] = [LeadOut.from_orm(l) for l in leads]

    return {
        "data": {
            "leads": leads_out,
            "meta": {
                "total": meta["total"],
                "page": meta["page"],
                "limit": meta["limit"],
                "pages": meta["pages"],
                "sector": sector,
                "city": city,
            },
        }
    }

@router.get("/my-leads", response_model=dict, dependencies=[Depends(role_required(["Technician"]))])
def get_technician_leads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(Lead).filter(Lead.assigned_technician_id == current_user.id)
    
    leads, meta = paginate(query.order_by(Lead.created_at.desc()), page, limit)

    leads_out = [LeadOut.from_orm(l) for l in leads]

    return {
        "data": {
            "leads": leads_out,
            "meta": meta
        }
    }
