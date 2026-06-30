from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import user_can_access_organization
from app.infrastructure.thingsboard.client import ThingsBoardClient
from app.modules.audit.service import AuditService
from app.modules.companies.models import Asset
from app.modules.devices.models import Device
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate, DeviceTelemetryRead, DeviceUpdate
from app.modules.users.models import User

TELEMETRY_KEYS = [
    "temperature",
    "temperatura",
    "battery",
    "bateria",
    "fuel",
    "combustivel",
    "rssi",
]


class DeviceService:
    def __init__(self, db: Session, thingsboard: ThingsBoardClient | None = None) -> None:
        self.repository = DeviceRepository(db)
        self.thingsboard = thingsboard or ThingsBoardClient()

    async def create_device(self, payload: DeviceCreate, actor: User) -> Device:
        asset = self._validate_device_scope(payload.organization_id, actor, payload.asset_id, payload.site_id)
        device = Device(
            organization_id=payload.organization_id,
            site_id=asset.site_id,
            asset_id=asset.id,
            thingsboard_device_id=f"pending-{uuid4()}",
            name=payload.name,
            label=payload.label,
            type=payload.type,
            attributes=payload.attributes,
            status="provisioning",
        )
        created = self.repository.create(device)

        try:
            tb_device = await self.thingsboard.create_device(
                name=payload.name,
                label=payload.label,
                device_type=payload.type,
            )
        except Exception:
            self.repository.update(created, {"status": "sync_failed"})
            raise
        tb_id = tb_device.get("id", {}).get("id")
        if not tb_id:
            self.repository.update(created, {"status": "sync_failed"})
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid ThingsBoard response")

        created = self.repository.update(created, {"thingsboard_device_id": tb_id, "status": "offline"})
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
        values = payload.model_dump(exclude_unset=True)
        target_asset_id = values.get("asset_id", device.asset_id)
        if not target_asset_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device asset is required")
        asset = self._validate_device_scope(device.organization_id, actor, target_asset_id, values.get("site_id"))
        values["asset_id"] = asset.id
        values["site_id"] = asset.site_id
        updated = self.repository.update(device, values)
        AuditService(self.repository.db).record(
            "device.updated",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="device",
            resource_id=updated.id,
            metadata=values,
        )
        return updated

    async def delete_device(self, device: Device, actor: User) -> Device:
        self._validate_device_scope(device.organization_id, actor, device.asset_id, device.site_id)
        if not device.thingsboard_device_id.startswith("pending-"):
            await self.thingsboard.delete_device(device.thingsboard_device_id)
        updated = self.repository.update(device, {"status": "deleted"})
        AuditService(self.repository.db).record(
            "device.deleted",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="device",
            resource_id=updated.id,
        )
        return updated

    async def get_telemetry(self, device: Device) -> DeviceTelemetryRead:
        simulated = self._simulated_telemetry(device)
        try:
            latest = await self.thingsboard.get_latest_telemetry(device.thingsboard_device_id, TELEMETRY_KEYS)
        except Exception:
            return simulated

        if not latest:
            return simulated

        updated_at = self._latest_timestamp(latest) or simulated.ultima_atualizacao
        return DeviceTelemetryRead(
            device_id=device.id,
            temperatura=self._read_float(latest, ["temperatura", "temperature"], simulated.temperatura),
            bateria=self._read_float(latest, ["bateria", "battery"], simulated.bateria),
            combustivel=self._read_float(latest, ["combustivel", "fuel"], simulated.combustivel),
            rssi=int(self._read_float(latest, ["rssi"], float(simulated.rssi))),
            ultima_atualizacao=updated_at,
            source="thingsboard",
        )

    def _validate_device_scope(
        self,
        organization_id: str,
        actor: User,
        asset_id: str,
        site_id: str | None = None,
    ) -> Asset:
        if not user_can_access_organization(self.repository.db, actor, organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        asset = self.repository.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset or asset.organization_id != organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset scope")
        if site_id and site_id != asset.site_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site scope")
        return asset

    def _simulated_telemetry(self, device: Device) -> DeviceTelemetryRead:
        seed = sum(ord(char) for char in device.id)
        return DeviceTelemetryRead(
            device_id=device.id,
            temperatura=round(18 + (seed % 180) / 10, 1),
            bateria=round(35 + (seed % 60), 1),
            combustivel=round(20 + (seed % 75), 1),
            rssi=-95 + (seed % 45),
            ultima_atualizacao=datetime.now(UTC),
            source="simulated",
        )

    def _read_float(self, latest: dict[str, Any], keys: list[str], default: float) -> float:
        for key in keys:
            samples = latest.get(key)
            if not samples:
                continue
            value = samples[0].get("value") if isinstance(samples[0], dict) else samples[0]
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return default

    def _latest_timestamp(self, latest: dict[str, Any]) -> datetime | None:
        timestamps: list[int] = []
        for samples in latest.values():
            if not samples or not isinstance(samples[0], dict):
                continue
            timestamp = samples[0].get("ts")
            if isinstance(timestamp, int):
                timestamps.append(timestamp)
        if not timestamps:
            return None
        return datetime.fromtimestamp(max(timestamps) / 1000, tz=UTC)
