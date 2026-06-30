from typing import Literal, TypeAlias

RoleName: TypeAlias = Literal[
    "platform_owner",
    "platform_admin",
    "partner_admin",
    "partner_technician",
    "organization_admin",
    "organization_operator",
    "read_only",
]

PLATFORM_ROLES = {"platform_owner", "platform_admin"}
PARTNER_ROLES = {"partner_admin", "partner_technician"}
ORGANIZATION_ROLES = {"organization_admin", "organization_operator"}

READ_PERMISSIONS = {
    "alerts:read",
    "assets:read",
    "dashboards:read",
    "devices:read",
    "organizations:read",
    "partners:read",
    "sites:read",
    "telemetry:read",
    "users:read",
    "workflows:read",
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "platform_owner": {
        "*",
    },
    "platform_admin": {
        "alerts:read",
        "alerts:write",
        "assets:read",
        "assets:write",
        "audit:read",
        "dashboards:read",
        "devices:read",
        "devices:write",
        "organizations:read",
        "organizations:write",
        "partners:read",
        "partners:write",
        "sites:read",
        "sites:write",
        "telemetry:read",
        "users:read",
        "users:write",
        "workflows:read",
        "workflows:write",
    },
    "partner_admin": {
        "alerts:read",
        "alerts:write",
        "assets:read",
        "assets:write",
        "dashboards:read",
        "devices:read",
        "devices:write",
        "organizations:read",
        "organizations:write",
        "sites:read",
        "sites:write",
        "telemetry:read",
        "users:read",
        "users:write",
        "workflows:read",
        "workflows:write",
    },
    "partner_technician": {
        "alerts:read",
        "alerts:write",
        "assets:read",
        "assets:write",
        "dashboards:read",
        "devices:read",
        "devices:write",
        "organizations:read",
        "sites:read",
        "sites:write",
        "telemetry:read",
        "workflows:read",
    },
    "organization_admin": {
        "alerts:read",
        "alerts:write",
        "assets:read",
        "assets:write",
        "dashboards:read",
        "devices:read",
        "devices:write",
        "organizations:read",
        "sites:read",
        "sites:write",
        "telemetry:read",
        "users:read",
        "users:write",
        "workflows:read",
    },
    "organization_operator": {
        "alerts:read",
        "alerts:write",
        "assets:read",
        "dashboards:read",
        "devices:read",
        "sites:read",
        "telemetry:read",
        "workflows:read",
    },
    "read_only": READ_PERMISSIONS,
}


def has_permission(role: str, permission: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, set())
    return "*" in permissions or permission in permissions


def is_platform_role(role: str) -> bool:
    return role in PLATFORM_ROLES


def is_partner_role(role: str) -> bool:
    return role in PARTNER_ROLES


def is_organization_role(role: str) -> bool:
    return role in ORGANIZATION_ROLES or role == "read_only"
