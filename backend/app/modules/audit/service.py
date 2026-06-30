from typing import Any

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.modules.users.models import User

SENSITIVE_KEYS = {
    "access_token",
    "authorization",
    "jwt",
    "password",
    "secret",
    "thingsboard_password",
    "thingsboard_token",
    "token",
}


def sanitize_metadata(value: dict[str, Any] | None) -> dict[str, Any]:
    if not value:
        return {}

    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        lowered = key.lower()
        if any(secret in lowered for secret in SENSITIVE_KEYS):
            sanitized[key] = "[redacted]"
        elif isinstance(item, dict):
            sanitized[key] = sanitize_metadata(item)
        else:
            sanitized[key] = item
    return sanitized


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        action: str,
        *,
        status: str = "success",
        actor: User | None = None,
        partner_id: str | None = None,
        organization_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_user_id=actor.id if actor else None,
            partner_id=partner_id or (actor.partner_id if actor else None),
            organization_id=organization_id or (actor.organization_id if actor else None),
            action=action,
            status=status,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_data=sanitize_metadata(metadata),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
