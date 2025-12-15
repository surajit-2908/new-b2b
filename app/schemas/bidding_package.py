from pydantic import BaseModel

from app.schemas.user import UserOut
from app.schemas.work_package import PackageBaseOut
from datetime import datetime


class biddingPackageCreate(BaseModel):
    work_package_id: int
    bidding_amount: float
    note: str = ""
    
class biddingPackageOut(BaseModel):
    id: int
    work_package: PackageBaseOut
    technician: UserOut
    bidding_amount: float
    note: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True    
