from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Numeric,
    ForeignKey,
    func,
    JSON,
)
from sqlalchemy.orm import relationship
from app.database import Base


class WorkPackage(Base):
    __tablename__ = "work_packages"

    id = Column(Integer, primary_key=True, index=True)

    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    package_number = Column(String(50), unique=True, index=True, nullable=False)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    bidding_status = Column(String(20), nullable=True)
    bidding_duration_days = Column(Integer, nullable=False) # pending,active,closed

    package_title = Column(Text, nullable=False)
    package_type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False)
    package_summary = Column(Text, nullable=False)
    custom_package_type = Column(Text, nullable=True)

    key_deliverables = Column(Text, nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    required_skills_ids = Column(JSON, nullable=False)
    primary_tools_ids = Column(JSON, nullable=False)
    required_tools_ids = Column(JSON, nullable=False)

    package_estimated_complexity = Column(Text, nullable=False)

    package_price_allocation = Column(Numeric, nullable=True)

    dependencies_ids =  Column(JSON, nullable=False)

    status = Column(String(100), nullable=True)  # draft / active
    draft_version = Column(Integer, nullable=True)

    last_saved_at = Column(DateTime, server_default=func.now(), nullable=True)

    # Relationship
    deal = relationship("Deal", back_populates="work_package", lazy="joined")
    package_type = relationship("PackageType", back_populates="work_package", lazy="joined")
    # bidding_packages = relationship("BiddingPackage", back_populates="work_package", cascade="all, delete-orphan")
