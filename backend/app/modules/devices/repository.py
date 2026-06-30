from sqlalchemy.orm import Session

from app.modules.devices.models import Device


class DeviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, organization_ids: list[str] | None = None) -> list[Device]:
        query = self.db.query(Device)
        if organization_ids is not None:
            query = query.filter(Device.organization_id.in_(organization_ids))
        return query.order_by(Device.created_at.desc()).all()

    def get_by_id(self, device_id: str) -> Device | None:
        return self.db.query(Device).filter(Device.id == device_id).first()

    def create(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def update(self, device: Device, values: dict) -> Device:
        for field, value in values.items():
            setattr(device, field, value)
        self.db.commit()
        self.db.refresh(device)
        return device
