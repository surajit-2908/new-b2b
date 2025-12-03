from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class SectorPackage(Base):
    __tablename__ = "sector_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)

    deal = relationship("Deal", back_populates="sector_package", lazy="joined")
