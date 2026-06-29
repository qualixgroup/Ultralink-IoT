from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    company_id: str
    name: str
    label: str | None = None
    type: str = "sensor"
    attributes: dict[str, Any] = Field(default_factory=dict)


class DeviceRead(BaseModel):
    id: str
    company_id: str
    thingsboard_device_id: str
    name: str
    label: str | None
    type: str
    status: str
    attributes: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
