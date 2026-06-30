"""consolidate multitenant foundation

Revision ID: 202606292200
Revises: 202606291200
Create Date: 2026-06-29 22:00:00
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202606292200"
down_revision: str | None = "202606291200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _new_id() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


def upgrade() -> None:
    bind = op.get_bind()

    sites = sa.table(
        "sites",
        sa.column("id", sa.String(36)),
        sa.column("organization_id", sa.String(36)),
        sa.column("name", sa.String(160)),
        sa.column("address", sa.String(255)),
        sa.column("status", sa.String(32)),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    assets = sa.table(
        "assets",
        sa.column("id", sa.String(36)),
        sa.column("organization_id", sa.String(36)),
        sa.column("site_id", sa.String(36)),
        sa.column("name", sa.String(160)),
        sa.column("type", sa.String(64)),
        sa.column("status", sa.String(32)),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    devices = sa.table(
        "devices",
        sa.column("id", sa.String(36)),
        sa.column("organization_id", sa.String(36)),
        sa.column("site_id", sa.String(36)),
        sa.column("asset_id", sa.String(36)),
    )
    users = sa.table("users", sa.column("id", sa.String(36)))
    partners = sa.table("partners", sa.column("id", sa.String(36)))
    organizations = sa.table("organizations", sa.column("id", sa.String(36)))
    audit_logs = sa.table(
        "audit_logs",
        sa.column("id", sa.String(36)),
        sa.column("actor_user_id", sa.String(36)),
        sa.column("partner_id", sa.String(36)),
        sa.column("organization_id", sa.String(36)),
    )

    def existing_site(site_id: str | None, organization_id: str) -> str | None:
        if not site_id:
            return None
        return bind.execute(
            sa.select(sites.c.id).where(
                sites.c.id == site_id,
                sites.c.organization_id == organization_id,
            )
        ).scalar_one_or_none()

    def ensure_site(organization_id: str) -> str:
        site_id = bind.execute(
            sa.select(sites.c.id).where(sites.c.organization_id == organization_id).limit(1)
        ).scalar_one_or_none()
        if site_id:
            return str(site_id)

        site_id = _new_id()
        bind.execute(
            sites.insert().values(
                id=site_id,
                organization_id=organization_id,
                name="Default Site",
                address=None,
                status="active",
                created_at=_now(),
            )
        )
        return site_id

    def existing_asset(asset_id: str | None, organization_id: str) -> tuple[str, str] | None:
        if not asset_id:
            return None
        row = bind.execute(
            sa.select(assets.c.id, assets.c.site_id).where(
                assets.c.id == asset_id,
                assets.c.organization_id == organization_id,
            )
        ).first()
        if not row:
            return None
        return str(row[0]), str(row[1])

    def create_asset(organization_id: str, site_id: str) -> str:
        asset_id = _new_id()
        bind.execute(
            assets.insert().values(
                id=asset_id,
                organization_id=organization_id,
                site_id=site_id,
                name="Default Asset",
                type="generic",
                status="active",
                created_at=_now(),
            )
        )
        return asset_id

    for row in bind.execute(
        sa.select(assets.c.id, assets.c.organization_id).where(assets.c.site_id.is_(None))
    ).mappings():
        bind.execute(
            assets.update()
            .where(assets.c.id == row["id"])
            .values(site_id=ensure_site(str(row["organization_id"])))
        )

    for row in bind.execute(
        sa.select(devices.c.id, devices.c.organization_id, devices.c.site_id, devices.c.asset_id).where(
            sa.or_(devices.c.site_id.is_(None), devices.c.asset_id.is_(None))
        )
    ).mappings():
        organization_id = str(row["organization_id"])
        asset = existing_asset(row["asset_id"], organization_id)
        if asset:
            target_asset_id, target_site_id = asset
        else:
            target_site_id = existing_site(row["site_id"], organization_id) or ensure_site(organization_id)
            target_asset_id = create_asset(organization_id, target_site_id)

        bind.execute(
            devices.update()
            .where(devices.c.id == row["id"])
            .values(asset_id=target_asset_id, site_id=target_site_id)
        )

    for table, column_name, target_table in [
        (audit_logs, "actor_user_id", users),
        (audit_logs, "partner_id", partners),
        (audit_logs, "organization_id", organizations),
    ]:
        for row in bind.execute(
            sa.select(table.c.id, table.c[column_name]).where(table.c[column_name].is_not(None))
        ).mappings():
            exists = bind.execute(
                sa.select(target_table.c.id).where(target_table.c.id == row[column_name])
            ).scalar_one_or_none()
            if not exists:
                bind.execute(table.update().where(table.c.id == row["id"]).values({column_name: None}))

    with op.batch_alter_table("assets") as batch_op:
        batch_op.alter_column("site_id", existing_type=sa.String(length=36), nullable=False)

    with op.batch_alter_table("devices") as batch_op:
        batch_op.alter_column("site_id", existing_type=sa.String(length=36), nullable=False)
        batch_op.alter_column("asset_id", existing_type=sa.String(length=36), nullable=False)

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.create_foreign_key("fk_audit_logs_actor_user_id_users", "users", ["actor_user_id"], ["id"])
        batch_op.create_foreign_key("fk_audit_logs_partner_id_partners", "partners", ["partner_id"], ["id"])
        batch_op.create_foreign_key(
            "fk_audit_logs_organization_id_organizations",
            "organizations",
            ["organization_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_constraint("fk_audit_logs_organization_id_organizations", type_="foreignkey")
        batch_op.drop_constraint("fk_audit_logs_partner_id_partners", type_="foreignkey")
        batch_op.drop_constraint("fk_audit_logs_actor_user_id_users", type_="foreignkey")

    with op.batch_alter_table("devices") as batch_op:
        batch_op.alter_column("asset_id", existing_type=sa.String(length=36), nullable=True)
        batch_op.alter_column("site_id", existing_type=sa.String(length=36), nullable=True)

    with op.batch_alter_table("assets") as batch_op:
        batch_op.alter_column("site_id", existing_type=sa.String(length=36), nullable=True)
