from typing import Optional
from sqlalchemy.orm import Session
from app.models.users import User

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_or_get_user(db: Session, email: str, name: str = None):
    user = get_user_by_email(db, email)
    if user:
        return user
    new_user = User(email=email, name=name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_otp_and_token(db: Session, user: User, otp: str, token: str) -> User:
    user.otp = otp
    user.verify_page_token = token
    db.commit()
    db.refresh(user)
    return user
