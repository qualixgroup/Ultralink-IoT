from fastapi import APIRouter, Depends

from app.common.dependencies import CurrentUser, DbSession, require_permission, visible_organization_ids
from app.modules.alerts.models import Alert
from app.modules.dashboards.schemas import DashboardSummary
from app.modules.devices.models import Device

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/summary", response_model=DashboardSummary, dependencies=[Depends(require_permission("dashboards:read"))])
def get_summary(db: DbSession, current_user: CurrentUser) -> DashboardSummary:
    devices_query = db.query(Device)
    alerts_query = db.query(Alert)
    organization_ids = visible_organization_ids(db, current_user)
    if organization_ids is not None:
        devices_query = devices_query.filter(Device.organization_id.in_(organization_ids))
        alerts_query = alerts_query.filter(Alert.organization_id.in_(organization_ids))

    devices = devices_query.all()
    return DashboardSummary(
        online=sum(1 for device in devices if device.status == "online"),
        offline=sum(1 for device in devices if device.status != "online"),
        alerts=alerts_query.filter(Alert.status == "open").count(),
        towers=sum(1 for device in devices if device.type == "tower"),
        generators=sum(1 for device in devices if device.type == "generator"),
        tanks=sum(1 for device in devices if device.type == "tank"),
        sensors=sum(1 for device in devices if device.type == "sensor"),
    )
