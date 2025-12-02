from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Numeric, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class WorkPackage(Base):
    __tablename__ = "work_packages"

    id = Column(Integer, primary_key=True, index=True)

    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)

    package_title = Column(Text, nullable=False)
    package_type = Column(String(150), nullable=False)
    package_summary = Column(Text, nullable=False)

    key_deliverables = Column(Text, nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=False)
    primary_tools = Column(Text, nullable=False)

    package_estimated_complexity = Column(Text, nullable=False)

    package_price_allocation = Column(Numeric, nullable=True)

    dependencies = Column(Text, nullable=False)  # stored as text (JSON string)

    status = Column(String(100), nullable=True)  # draft / active
    draft_version = Column(Integer, nullable=True)

    last_saved_at = Column(DateTime, server_default=func.now(), nullable=True)

    # Relationship
    deal = relationship("Deal", back_populates="work_package", lazy="joined")
    