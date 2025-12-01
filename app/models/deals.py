from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class Deals(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    client_name = Column(Text, nullable=False)
    primary_contact_name = Column(String(150), nullable=False)
    primary_contact_email = Column(String(100), nullable=False)
    primary_contact_phone = Column(String(50), nullable=True)

    industry = Column(String(100), nullable=True)

    sector_package = Column(String(150), nullable=False)

    deal_name = Column(Text, nullable=False)
    salesperson_name = Column(String(150), nullable=False)

    deal_close_date = Column(DateTime, nullable=False)
    expected_start_date = Column(DateTime, nullable=True)
    expected_end_date_or_deadline = Column(DateTime, nullable=True)

    client_approved_scope_summary = Column(Text, nullable=False)
    special_terms = Column(Text, nullable=True)

    status = Column(String(100), nullable=True)   # draft / active
    draft_version = Column(Integer, nullable=True)

    last_saved_at = Column(DateTime, server_default=func.now(), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship (optional)
    lead = relationship("Leads", back_populates="deals", lazy="joined")