from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str  

class UserUpdate(UserBase):
    password: Optional[str] = None 

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        
class UserResponse(BaseModel):
    message: str
    user: UserOut

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    accessToken: str
    message: str
    user: dict
