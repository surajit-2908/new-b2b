from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class TechnicalContext(Base):
    __tablename__ = "technical_contexts"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    client_main_systems = Column(Text, nullable=False)
    integration_targets = Column(Text, nullable=True)
    tools_in_scope = Column(Text, nullable=False)
    access_required_list = Column(Text, nullable=False)
    credential_provision_method = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    # relationships
    deal = relationship("Deal", back_populates="technical_context", lazy="joined")
