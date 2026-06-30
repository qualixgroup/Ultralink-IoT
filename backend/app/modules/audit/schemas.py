from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: str
    actor_user_id: str | None
    partner_id: str | None
    organization_id: str | None
    action: str
    status: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    user_agent: str | None
    event_data: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
