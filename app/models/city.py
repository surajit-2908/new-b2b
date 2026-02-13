from sqlalchemy import Column, Integer, String, DateTime, Float, func
from app.database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False, index=True)

    state = Column(String(150), nullable=True, index=True)
    geoid = Column(String(20), nullable=True, unique=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
