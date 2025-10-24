from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import LoginRequest, LoginResponse
from app.models.user import User
from app import auth
from app.crud import user as crud_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.verify_password(payload.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = auth.create_access_token({"sub": user.email})

    return {
        "accessToken": token,
        "message": "Logged in successfully",
        "user": {"id": user.id, "email": user.email, "name": user.name}
    }
