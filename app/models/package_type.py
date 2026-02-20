from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship


class PackageType(Base):
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship


    work_packages = relationship("WorkPackage", back_populates="package_type", lazy="joined")
