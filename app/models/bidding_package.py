from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime, Text, func
from app.database import Base

class BiddingPackage(Base):
    __tablename__ = "bidding_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    work_package_id = Column(Integer, ForeignKey("work_packages.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bidding_amount = Column(Float, nullable=False) 
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())