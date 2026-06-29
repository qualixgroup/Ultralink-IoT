from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    company_id: str
    email: EmailStr
    full_name: str
    password: str
    role: str = "operator"


class UserRead(BaseModel):
    id: str
    company_id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
