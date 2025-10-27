from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String(255), nullable=False, index=True)
    sector = Column(String(255), nullable=False, index=True)
    city = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    summary = Column(String(1024), nullable=True)
    lead_status = Column(String(50), default="new")
    follow_up_status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
