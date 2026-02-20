from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    client_name = Column(Text, nullable=False)
    primary_contact_name = Column(String(150), nullable=False)
    primary_contact_email = Column(String(100), nullable=False)
    primary_contact_phone = Column(String(50), nullable=True)

    industry = Column(String(100), nullable=True)

    # NEW FIELD — store ID instead of name
    sector_package_id = Column(Integer, ForeignKey("sector_packages.id"), nullable=False)

    # Only used if “Other (Specify)”
    custom_sector_package = Column(String(200), nullable=True)

    deal_name = Column(Text, nullable=False)
    salesperson_name = Column(String(150), nullable=True)

    deal_close_date = Column(DateTime, nullable=True)
    expected_start_date = Column(DateTime, nullable=True)
    expected_end_date_or_deadline = Column(DateTime, nullable=True)
    max_duration = Column(Integer, nullable=False)

    client_approved_scope_summary = Column(Text, nullable=False)
    special_terms = Column(Text, nullable=True)

    status = Column(String(100), nullable=True)   # draft / active
    draft_version = Column(Integer, nullable=True)

    last_saved_at = Column(DateTime, server_default=func.now(), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    lead = relationship("Lead", back_populates="deals")
    work_packages = relationship("WorkPackage", back_populates="deal", cascade="all, delete-orphan")
    technical_context = relationship("TechnicalContext", back_populates="deal")
    communication = relationship("Communication", back_populates="deal")  
    internal_note = relationship("InternalNote", back_populates="deal")  
    sector_package = relationship("SectorPackage", back_populates="deal")  
