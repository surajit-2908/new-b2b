from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.sector_package import SectorPackage
from app.schemas.deal import DealCreate
from app.schemas.sector_package import SectorPackageResponse
from app.auth import role_required

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("/sector-package", response_model=list[SectorPackageResponse])
def list_sector_packages(db: Session = Depends(get_db)):
    """
    Fetch all sector packages for dropdown.
    """
    packages = db.query(SectorPackage).order_by(SectorPackage.id.asc()).all()
    return packages


@router.post(
    "/save",
    response_model=dict,
    dependencies=[Depends(role_required(["Admin", "User"]))],
)
def create_or_update_deal(data: DealCreate, db: Session = Depends(get_db)):

    # Validate lead
    lead = (
        db.query(Lead)
        .filter(Lead.id == data.lead_id)
        .filter(Lead.lead_status.notin_(["Not interested", "Triple Positive"]))
        .first()
    )
    if not lead:
        raise HTTPException(404, "Lead not found or not eligible")

    # Get “Other (Specify)” ID
    other_pkg = (
        db.query(SectorPackage)
        .filter(SectorPackage.name == "Other (Specify)")
        .first()
    )
    other_pkg_id = other_pkg.id if other_pkg else None

    # Check existing deal
    existing_deal = db.query(Deal).filter(Deal.lead_id == data.lead_id).first()

    # Determine custom sector text
    custom_text = (
        data.custom_sector_package
        if data.sector_package_id == other_pkg_id
        else None
    )

    if existing_deal:
        # -------- UPDATE --------
        existing_deal.client_name = data.client_name
        existing_deal.primary_contact_name = data.primary_contact_name
        existing_deal.primary_contact_email = data.primary_contact_email
        existing_deal.primary_contact_phone = data.primary_contact_phone
        existing_deal.industry = data.industry

        existing_deal.sector_package_id = data.sector_package_id
        existing_deal.custom_sector_package = custom_text

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

    # -------- CREATE --------
    new_deal = Deal(
        lead_id=data.lead_id,
        client_name=data.client_name,
        primary_contact_name=data.primary_contact_name,
        primary_contact_email=data.primary_contact_email,
        primary_contact_phone=data.primary_contact_phone,
        industry=data.industry,

        sector_package_id=data.sector_package_id,
        custom_sector_package=custom_text,

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
