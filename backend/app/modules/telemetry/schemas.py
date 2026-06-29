from typing import Any

from pydantic import BaseModel


class TelemetryResponse(BaseModel):
    device_id: str
    thingsboard_device_id: str
    values: dict[str, Any]
