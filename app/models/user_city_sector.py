from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class UserCitySector(Base):
    __tablename__ = "user_city_sector"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_city_sectors")

    __table_args__ = (
        UniqueConstraint("sector", "city", name="unique_sector_city"),
    )