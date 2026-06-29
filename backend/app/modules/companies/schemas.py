from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    document: str | None = None


class CompanyRead(BaseModel):
    id: str
    name: str
    document: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
