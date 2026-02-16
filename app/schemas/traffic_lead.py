from pydantic import BaseModel, EmailStr

class TrafficLeadCreate(BaseModel):
    city: str
    sector: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    summary: str | None = None 