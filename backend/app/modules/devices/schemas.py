from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    organization_id: str
    site_id: str | None = None
    asset_id: str | None = None
    name: str
    label: str | None = None
    type: str = "sensor"
    attributes: dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    site_id: str | None = None
    asset_id: str | None = None
    name: str | None = None
    label: str | None = None
    type: str | None = None
    status: str | None = None
    attributes: dict[str, Any] | None = None


class DeviceRead(BaseModel):
    id: str
    organization_id: str
    site_id: str | None
    asset_id: str | None
    name: str
    label: str | None
    type: str
    status: str
    attributes: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
