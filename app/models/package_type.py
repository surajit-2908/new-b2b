from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class PackageType(Base):
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
