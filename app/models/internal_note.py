from sqlalchemy import (
    Column, Integer, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class InternalNote(Base):
    __tablename__ = "internal_notes"

    id = Column(Integer, primary_key=True, index=True)

    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)

    internal_risks_and_warnings = Column(Text, nullable=True)
    internal_margin_sensitivity = Column(Text, nullable=False) #Low/Medium/High
    internal_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    deal = relationship("Deal", back_populates="internal_notes", lazy="joined")
    