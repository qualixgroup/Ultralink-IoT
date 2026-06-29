from fastapi import APIRouter

from app.common.dependencies import CurrentUser, DbSession
from app.modules.alerts.models import Alert
from app.modules.dashboards.schemas import DashboardSummary
from app.modules.devices.models import Device

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: DbSession, current_user: CurrentUser) -> DashboardSummary:
    devices_query = db.query(Device)
    alerts_query = db.query(Alert)
    if current_user.role != "owner":
        devices_query = devices_query.filter(Device.company_id == current_user.company_id)
        alerts_query = alerts_query.filter(Alert.company_id == current_user.company_id)

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
