from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.schemas.user import UserOut, UserCreate, UserUpdate, UserResponse, UserWithCitySectorOut
from app.utils.email import send_user_email
from passlib.context import CryptContext
import os
from app.auth import role_required
from app.utils.pagination import paginate

router = APIRouter(prefix="/user", tags=["User"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_FOLDER = "./uploads/profile_pictures"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------------------------
# CRUD OPERATIONS
# ----------------------------------------------------------------------

@router.get("", response_model=dict, dependencies=[Depends(role_required(["Admin"]))])
def get_all_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    keyword: str = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(
        None,
        description="Filter by role",
        regex="^(Admin|Sales|Technician)$"
    )
):
    query = db.query(User).options(selectinload(User.user_city_sectors))
    if keyword:
        query = query.filter(or_(
            User.name.ilike(f"%{keyword}%"),
            User.email.ilike(f"%{keyword}%")
        ))
        
    if role:
        query = query.filter(User.role == role)

    query = query.order_by(User.created_at.desc())
    
    users, meta = paginate(query.order_by(User.created_at.desc()), page, limit)

    users_out: List[UserWithCitySectorOut] = [UserWithCitySectorOut.from_orm(u) for u in users]

    return {
        "data": {
            "users": users_out,
            "meta": {
                "total": meta["total"],
                "page": meta["page"],
                "limit": meta["limit"],
                "pages": meta["pages"],
                "query": keyword,
            }
        }
    }


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(role_required(["Admin"]))])
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

ALLOWED_ROLES = ["Admin", "Sales", "Technician"]
@router.post("/create", response_model=UserResponse, dependencies=[Depends(role_required(["Admin"]))])
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if user_data.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed roles are: {', '.join(ALLOWED_ROLES)}"
        )
        
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash the password received from frontend
    hashed_password = pwd_context.hash(user_data.password)

    new_user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
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


@router.put("/update/{user_id}", response_model=UserResponse, dependencies=[Depends(role_required(["Admin"]))])
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
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
        
    if user.role != user_data.role:
        if user_data.role not in ALLOWED_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Allowed roles are: {', '.join(ALLOWED_ROLES)}"
            )
        user.role = user_data.role
        updated_fields.append("Role")
        
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

@router.delete("/delete/{user_id}", dependencies=[Depends(role_required(["Admin"]))])
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User deleted successfully."}

# ----------------------------------------------------------------------
# PROFILE MANAGEMENT
# ----------------------------------------------------------------------

@router.get("/me", response_model=UserOut, dependencies=[Depends(role_required(["Admin", "Sales"]))])
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
