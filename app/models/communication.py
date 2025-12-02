from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)

    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)

    client_project_contact_name = Column(Text, nullable=False)
    client_project_contact_email = Column(Text, nullable=False)
    preferred_channel = Column(Text, nullable=True)
    update_frequency = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # relationships
    deal = relationship("Deal", back_populates="communication", lazy="joined")
