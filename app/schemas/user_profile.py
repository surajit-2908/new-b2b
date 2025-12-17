from pydantic import BaseModel, ConfigDict, EmailStr
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

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
