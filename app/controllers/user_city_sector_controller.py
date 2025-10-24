from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_city_sector import UserCitySector
from app.models.lead import Lead
from app.schemas.lead import LeadOut
from app.models.user import User
from app.schemas.user_city_sector_schema import UserCitySectorCreate, UserCitySectorOut

router = APIRouter(prefix="/assign-user", tags=["User Sector Assignment"])


@router.post("/", response_model=UserCitySectorOut)
def assign_sector_city(data: UserCitySectorCreate, db: Session = Depends(get_db)):
    # Verify user exists
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


@router.get("/leads/{user_id}", response_model=dict)
def get_user_assigned_leads(user_id: int, db: Session = Depends(get_db)):
    assignments = db.query(UserCitySector).filter(UserCitySector.user_id == user_id).all()
    if not assignments:
        raise HTTPException(status_code=404, detail="No sector-city assignments found for this user.")

    leads_data = []
    for assignment in assignments:
        leads = db.query(Lead).filter(
            Lead.sector == assignment.sector,
            Lead.city == assignment.city
        ).all()

        # ✅ Convert ORM objects to LeadOut schema
        serialized_leads = [LeadOut.from_orm(lead) for lead in leads]

        leads_data.append({
            "sector": assignment.sector,
            "city": assignment.city,
            "leads": serialized_leads
        })

    return {"data": leads_data}

