from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class LeadFreeNotes(Base):
    __tablename__= "lead_free_notes"
    
    id= Column(Integer, primary_key=True, index=True)
    notes = Column(Text, nullable=False)
    
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
   
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    
    created_user = relationship("User", foreign_keys=[created_by])
    updated_user = relationship("User", foreign_keys=[updated_by])