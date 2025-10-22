from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    role = Column(String(255), default='User')
    password = Column(String(255), nullable=False)  # hashed password
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def verify_password(self, password: str) -> bool:
        """Verify plain password against hashed password stored in `password` field"""
        return pwd_context.verify(password, self.password)

    def set_password(self, password: str):
        """Hash and set the password"""
        self.password = pwd_context.hash(password)
