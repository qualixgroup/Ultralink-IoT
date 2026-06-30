from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dependencies import (
    CurrentUser,
    DbSession,
    require_permission,
    user_can_access_organization,
    visible_organization_ids,
)
from app.modules.alerts.models import Alert
from app.modules.alerts.schemas import AlertCreate, AlertRead
from app.modules.audit.service import AuditService
from app.modules.devices.repository import DeviceRepository

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead], dependencies=[Depends(require_permission("alerts:read"))])
def list_alerts(db: DbSession, current_user: CurrentUser) -> list[Alert]:
    query = db.query(Alert)
    organization_ids = visible_organization_ids(db, current_user)
    if organization_ids is not None:
        query = query.filter(Alert.organization_id.in_(organization_ids))
    return query.order_by(Alert.created_at.desc()).all()


@router.post("", response_model=AlertRead, status_code=201, dependencies=[Depends(require_permission("alerts:write"))])
def create_alert(payload: AlertCreate, db: DbSession, current_user: CurrentUser) -> Alert:
    if not user_can_access_organization(db, current_user, payload.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    if payload.device_id:
        device = DeviceRepository(db).get_by_id(payload.device_id)
        if not device or device.organization_id != payload.organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid device scope")
    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    AuditService(db).record(
        "alert.created",
        actor=current_user,
        organization_id=alert.organization_id,
        resource_type="alert",
        resource_id=alert.id,
        metadata={"severity": alert.severity},
    )
    return alert
