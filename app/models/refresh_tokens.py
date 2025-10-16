from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base

class RefreshToken(Base):
    __tablename__ = 'RefreshToken'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.id"))
    refresh_token = Column(String)
    expires_at = Column(DateTime)