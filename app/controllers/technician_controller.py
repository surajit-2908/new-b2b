from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.lead import Lead
from app.models.package_type import PackageType
from app.models.skill import Skill
from app.models.tool import Tool
from app.models.work_package import WorkPackage
from app.schemas.bidding_package import biddingPackageCreate, biddingPackageOut
from app.schemas.lead import LeadOut
from app.auth import role_required

from app.models.user import User
from app.models.bidding_package import BiddingPackage
from app.auth import get_current_user
from app.schemas.work_package import PackageBaseOut
from app.utils.pagination import paginate

router = APIRouter(prefix="/technician", tags=["Technician"])


@router.get(
    "/leads",
    response_model=dict,
    dependencies=[Depends(role_required(["Technician", "Admin"]))],
)
def get_unassigned_triple_positive_leads(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Leads per page"),
    sector: str | None = Query(None, description="Filter by business sector"),
    city: str | None = Query(None, description="Filter by city"),
):
    """
    List leads where:
    - lead_status = 'Triple Positive'
    - assigned_technician_id IS NULL
    """
    query = db.query(Lead).filter(
        Lead.lead_status == "Triple Positive", Lead.assigned_technician_id.is_(None)
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


@router.get(
    "/my-leads",
    response_model=dict,
    dependencies=[Depends(role_required(["Technician"]))],
)
def get_technician_leads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    query = db.query(Lead).filter(Lead.assigned_technician_id == current_user.id)

    leads, meta = paginate(query.order_by(Lead.created_at.desc()), page, limit)

    leads_out = [LeadOut.from_orm(l) for l in leads]

    return {"data": {"leads": leads_out, "meta": meta}}


@router.post(
    "/save-bidding",
    response_model=dict,
    dependencies=[Depends(role_required(["Technician","Admin"]))],
)
def save_bidding_package(
    bidding_data: biddingPackageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_work_package = (
        db.query(WorkPackage)
        .filter(WorkPackage.id == bidding_data.work_package_id)
        .first()
    )
    if not valid_work_package:
        raise HTTPException(status_code=404, detail="Invalid work package ID.")

    existing_package = (
        db.query(BiddingPackage)
        .filter(
            BiddingPackage.work_package_id == bidding_data.work_package_id,
            BiddingPackage.technician_id == current_user.id,
        )
        .first()
    )

    if existing_package:
        existing_package.bidding_amount = bidding_data.bidding_amount
        existing_package.note = bidding_data.note
        db.commit()
        db.refresh(existing_package)
        return {"message": "Bidding package updated successfully"}
    else:
        new_bidding = BiddingPackage(
            work_package_id=bidding_data.work_package_id,
            technician_id=current_user.id,
            bidding_amount=bidding_data.bidding_amount,
            note=bidding_data.note,
        )
        db.add(new_bidding)
        db.commit()

        return {"message": "Bidding package saved successfully"}


@router.get("/get-bidding", response_model=biddingPackageOut)
def get_bidding_package(
    work_package_id: int,
    technician_id: int,
    db: Session = Depends(get_db),
):
    bidding_package = (
        db.query(BiddingPackage)
        .filter(
            BiddingPackage.work_package_id == work_package_id,
            BiddingPackage.technician_id == technician_id,
        )
        .first()
    )

    if not bidding_package:
        raise HTTPException(status_code=404, detail="Bidding package not found.")

    technician = db.query(User).filter(User.id == bidding_package.technician_id).first()
    work_package = (
        db.query(WorkPackage)
        .filter(WorkPackage.id == bidding_package.work_package_id)
        .first()
    )

    dependencies = []
    if work_package.dependencies_ids:
        dependencies = (
            db.query(PackageType)
            .filter(PackageType.id.in_(work_package.dependencies_ids))
            .all()
        )

    skills = []
    if work_package.required_skills_ids:
        skills = (
            db.query(Skill).filter(Skill.id.in_(work_package.required_skills_ids)).all()
        )

    tools = []
    if work_package.primary_tools_ids:
        tools = db.query(Tool).filter(Tool.id.in_(work_package.primary_tools_ids)).all()

    work_package_out = PackageBaseOut(
        id=work_package.id,
        package_title=work_package.package_title,
        package_type=work_package.package_type,
        package_summary=work_package.package_summary,
        custom_package_type=work_package.custom_package_type,
        key_deliverables=work_package.key_deliverables,
        acceptance_criteria=work_package.acceptance_criteria,
        required_skills=skills,
        primary_tools=tools,
        dependencies=dependencies,
        package_estimated_complexity=work_package.package_estimated_complexity,
        package_price_allocation=work_package.package_price_allocation,
    )

    package = biddingPackageOut(
        id=bidding_package.id,
        work_package=work_package_out,
        technician=technician,
        bidding_amount=bidding_package.bidding_amount,
        note=bidding_package.note,
        created_at=bidding_package.created_at,
        updated_at=bidding_package.updated_at,
    )

    return package
