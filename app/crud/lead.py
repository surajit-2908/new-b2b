from sqlalchemy.orm import Session
from app.models.lead import Lead
from typing import List

def get_leads_by_sector_city(db: Session, sector: str, city: str) -> List[Lead]:
    return db.query(Lead).filter(Lead.sector==sector, Lead.city==city).all()

def delete_leads_by_sector_city(db: Session, sector: str, city: str):
    db.query(Lead).filter(Lead.sector==sector, Lead.city==city).delete()
    db.commit()

def create_lead(db: Session, lead_data: dict) -> Lead:
    lead = Lead(**lead_data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
