from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import exists
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.deal import Deal
from app.models.lead import Lead
from app.models.package_type import PackageType
from app.models.skill import Skill
from app.models.tool import Tool
from app.models.work_package import WorkPackage
from app.schemas.bidding_package import biddingPackageCreate, biddingPackageOut
from app.schemas.deal import DealOut
from app.schemas.lead import LeadOut
from app.auth import role_required

from app.models.user import User
from app.models.bidding_package import BiddingPackage
from app.auth import get_current_user
from app.schemas.work_package import PackageBaseOut, TechnicianPackageOut
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
    dependencies=[Depends(role_required(["Technician", "Admin"]))],
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
    
    closed_bid_work_package = (
        db.query(WorkPackage)
        .filter(WorkPackage.id == bidding_data.work_package_id, WorkPackage.bidding_status == "Closed")
        .first()
    )
    
    if closed_bid_work_package:
        raise HTTPException(status_code=400, detail="Bidding for this work package is closed.")
    

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

    required_tools = []

    if work_package.required_tools_ids:
        required_tools = (
            db.query(Tool).filter(Tool.id.in_(work_package.required_tools_ids)).all()
        )

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
        required_tools=required_tools,
        dependencies=dependencies,
        package_estimated_complexity=work_package.package_estimated_complexity,
        package_price_allocation=work_package.package_price_allocation,
        bidding_duration_days=work_package.bidding_duration_days,
        bidding_status=work_package.bidding_status,
        assigned_technician=technician,
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


@router.get(
    "/packages",
    response_model=dict[str, list[PackageBaseOut]],
    dependencies=[Depends(role_required(["Technician"]))],
)
def get_packages_for_technician(
    tab_name: str = Query(..., pattern="^(new|active|awarded|closed)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    technician_id = user.id

    base_query = (
        db.query(WorkPackage, Deal.lead_id)
        .join(Deal, Deal.id == WorkPackage.deal_id)
    )

    match tab_name:

        # 🆕 NEW
        # Not expired + technician has NOT bid
        case "new":
            query = (
                base_query
                .filter(
                    WorkPackage.bidding_status == "Active",
                    ~db.query(BiddingPackage.id)
                    .filter(
                        BiddingPackage.work_package_id == WorkPackage.id,
                        BiddingPackage.technician_id == technician_id,
                    )
                    .exists(),
                )
            )

        # 🔵 ACTIVE
        # Technician has bid + not expired
        case "Active":
            query = (
                base_query
                .join(
                    BiddingPackage,
                    BiddingPackage.work_package_id == WorkPackage.id,
                )
                .filter(
                    WorkPackage.bidding_status == "Active",
                    BiddingPackage.technician_id == technician_id,
                )
                .distinct()
            )

        # 🟢 AWARDED
        # Assigned to current technician
        case "awarded":
            query = base_query.filter(
                WorkPackage.assigned_technician_id == technician_id
            )

        # 🔴 CLOSED
        # Awarded to someone else + technician had bid
        case "Closed":
            query = (
                base_query
                .join(
                    BiddingPackage,
                    BiddingPackage.work_package_id == WorkPackage.id,
                )
                .filter(
                    WorkPackage.bidding_status == "Closed",
                    BiddingPackage.technician_id == technician_id,
                    WorkPackage.assigned_technician_id != technician_id,
                )
                .distinct()
            )

    packages = query.order_by(WorkPackage.id.desc()).all()

    formatted_packages: list[TechnicianPackageOut] = []

    for pkg, lead_id in packages:

        is_placed_bidding = (
            db.query(BiddingPackage)
            .filter(
                BiddingPackage.work_package_id == pkg.id,
                BiddingPackage.technician_id == technician_id,
            )
            .first()
            is not None
        )

        formatted_packages.append(
            TechnicianPackageOut(
                id=pkg.id,
                lead_id=lead_id,  # ✅ HERE
                package_title=pkg.package_title,
                package_type=pkg.package_type,
                package_summary=pkg.package_summary,
                custom_package_type=pkg.custom_package_type,
                key_deliverables=pkg.key_deliverables,
                acceptance_criteria=pkg.acceptance_criteria,
                required_skills=db.query(Skill).filter(
                    Skill.id.in_(pkg.required_skills_ids)
                ).all() if pkg.required_skills_ids else [],
                primary_tools=db.query(Tool).filter(
                    Tool.id.in_(pkg.primary_tools_ids)
                ).all() if pkg.primary_tools_ids else [],
                required_tools=db.query(Tool).filter(
                    Tool.id.in_(pkg.required_tools_ids)
                ).all() if pkg.required_tools_ids else [],
                dependencies=db.query(PackageType).filter(
                    PackageType.id.in_(pkg.dependencies_ids)
                ).all() if pkg.dependencies_ids else [],
                package_estimated_complexity=pkg.package_estimated_complexity,
                package_price_allocation=pkg.package_price_allocation,
                bidding_duration_days=pkg.bidding_duration_days,
                bidding_status=pkg.bidding_status,
                assigned_technician=(
                    db.query(User)
                    .filter(User.id == pkg.assigned_technician_id)
                    .first()
                    if pkg.assigned_technician_id
                    else None
                ),
                user_bidding_placed=is_placed_bidding,
            )
        )

    return {"data": formatted_packages}

