from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(
        from_attributes=True,
    )
    
