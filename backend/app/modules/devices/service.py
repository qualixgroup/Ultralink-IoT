from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.thingsboard.client import ThingsBoardClient
from app.modules.devices.models import Device
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate


class DeviceService:
    def __init__(self, db: Session, thingsboard: ThingsBoardClient | None = None) -> None:
        self.repository = DeviceRepository(db)
        self.thingsboard = thingsboard or ThingsBoardClient()

    async def create_device(self, payload: DeviceCreate) -> Device:
        tb_device = await self.thingsboard.create_device(
            name=payload.name,
            label=payload.label,
            device_type=payload.type,
        )
        tb_id = tb_device.get("id", {}).get("id")
        if not tb_id:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid ThingsBoard response")

        device = Device(
            company_id=payload.company_id,
            thingsboard_device_id=tb_id,
            name=payload.name,
            label=payload.label,
            type=payload.type,
            attributes=payload.attributes,
        )
        return self.repository.create(device)
