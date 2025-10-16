from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfileResponse(BaseModel):
    id: int
    name: Optional[str]
    accountEmail: EmailStr
    profilePictureUrl: Optional[str]
    userCode: Optional[str]
    shippingMethod: Optional[str]
    discountPercentage: Optional[float]
    invoiceEmail: Optional[EmailStr]

    class Config:
        from_attributes = True
        populate_by_name = True
