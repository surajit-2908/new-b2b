from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.users import User
from app.auth import get_current_user
from app.schemas.user import UserOut, UserCreate, UserUpdate, UserResponse
from app.utils.email import send_user_email
from passlib.context import CryptContext
import os
import shutil

router = APIRouter(prefix="/user", tags=["User"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_FOLDER = "./uploads/profile_pictures"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------------------------
# CRUD OPERATIONS
# ----------------------------------------------------------------------

@router.get("/", response_model=dict)
def get_all_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: str = Query(None, description="Search by name or email")
):
    query = db.query(User)
    if keyword:
        query = query.filter(or_(
            User.name.ilike(f"%{keyword}%"),
            User.email.ilike(f"%{keyword}%")
        ))

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    users_out: List[UserOut] = [UserOut.from_orm(u) for u in users]

    return {
        "data": {
            "users": users_out,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
                "query": keyword,
            }
        }
    }


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/create", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash the password received from frontend
    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send email with password if needed
    # send_user_email(
    #     to_email=new_user.email,
    #     name=new_user.name or "",
    #     email=new_user.email,
    #     password=user_data.password,
    #     action="created"
    # )
    
    return {
        "message": "User created successfully.",
        "user": UserOut.from_orm(new_user)
    }


@router.put("/update/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_fields = []
    if user.name != user_data.name:
        user.name = user_data.name
        updated_fields.append("Name")
    if user.email != user_data.email:
        user.email = user_data.email
        updated_fields.append("Email")
    if user_data.password:
        user.password = pwd_context.hash(user_data.password)
        updated_fields.append("Password")

    db.commit()
    db.refresh(user)

    # if updated_fields:
    #     send_user_email(
    #         to_email=user.email,
    #         name=user.name,
    #         email=user.email,
    #         password=user_data.password if "Password" in updated_fields else None,
    #         action="updated",
    #         updated_fields=updated_fields
    #     )
    
    return {
        "message": "User updated successfully.",
        "user": UserOut.from_orm(user)
    }

@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User deleted successfully."}

# ----------------------------------------------------------------------
# PROFILE MANAGEMENT
# ----------------------------------------------------------------------

@router.get("/me", response_model=UserOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
