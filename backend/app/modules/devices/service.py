from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import user_can_access_organization
from app.infrastructure.thingsboard.client import ThingsBoardClient
from app.modules.audit.service import AuditService
from app.modules.companies.models import Asset, Site
from app.modules.devices.models import Device
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate, DeviceUpdate
from app.modules.users.models import User


class DeviceService:
    def __init__(self, db: Session, thingsboard: ThingsBoardClient | None = None) -> None:
        self.repository = DeviceRepository(db)
        self.thingsboard = thingsboard or ThingsBoardClient()

    async def create_device(self, payload: DeviceCreate, actor: User) -> Device:
        self._validate_device_scope(payload.organization_id, actor, payload.site_id, payload.asset_id)
        tb_device = await self.thingsboard.create_device(
            name=payload.name,
            label=payload.label,
            device_type=payload.type,
        )
        tb_id = tb_device.get("id", {}).get("id")
        if not tb_id:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid ThingsBoard response")

        device = Device(
            organization_id=payload.organization_id,
            site_id=payload.site_id,
            asset_id=payload.asset_id,
            thingsboard_device_id=tb_id,
            name=payload.name,
            label=payload.label,
            type=payload.type,
            attributes=payload.attributes,
        )
        created = self.repository.create(device)
        AuditService(self.repository.db).record(
            "device.created",
            actor=actor,
            organization_id=created.organization_id,
            resource_type="device",
            resource_id=created.id,
            metadata={"name": created.name, "type": created.type},
        )
        return created

    def update_device(self, device: Device, payload: DeviceUpdate, actor: User) -> Device:
        self._validate_device_scope(device.organization_id, actor, payload.site_id, payload.asset_id)
        updated = self.repository.update(device, payload.model_dump(exclude_unset=True))
        AuditService(self.repository.db).record(
            "device.updated",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="device",
            resource_id=updated.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return updated

    def delete_device(self, device: Device, actor: User) -> Device:
        self._validate_device_scope(device.organization_id, actor)
        updated = self.repository.update(device, {"status": "deleted"})
        AuditService(self.repository.db).record(
            "device.deleted",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="device",
            resource_id=updated.id,
        )
        return updated

    def _validate_device_scope(
        self,
        organization_id: str,
        actor: User,
        site_id: str | None = None,
        asset_id: str | None = None,
    ) -> None:
        if not user_can_access_organization(self.repository.db, actor, organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        if site_id:
            site = self.repository.db.query(Site).filter(Site.id == site_id).first()
            if not site or site.organization_id != organization_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site scope")

        if asset_id:
            asset = self.repository.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset or asset.organization_id != organization_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset scope")
