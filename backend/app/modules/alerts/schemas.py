from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
    organization_id: str
    device_id: str | None = None
    severity: str = "warning"
    message: str


class AlertRead(BaseModel):
    id: str
    organization_id: str
    device_id: str | None
    severity: str
    message: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
