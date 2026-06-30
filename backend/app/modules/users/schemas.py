from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

RoleName = Literal[
    "platform_owner",
    "platform_admin",
    "partner_admin",
    "partner_technician",
    "organization_admin",
    "organization_operator",
    "read_only",
]


class UserCreate(BaseModel):
    partner_id: str | None = None
    organization_id: str | None = None
    email: EmailStr
    full_name: str
    password: str
    role: RoleName = "read_only"


class UserUpdate(BaseModel):
    partner_id: str | None = None
    organization_id: str | None = None
    full_name: str | None = None
    role: RoleName | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    id: str
    partner_id: str | None
    organization_id: str | None
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
