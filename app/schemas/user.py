from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str  
    role: Optional[str] = "Sales"

class UserUpdate(UserBase):
    password: Optional[str] = None 
    role: Optional[str] = "Sales"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )
        
class UserResponse(BaseModel):
    message: str
    user: UserOut

    model_config = ConfigDict(
        from_attributes=True,
    )
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    accessToken: str
    message: str
    user: dict
