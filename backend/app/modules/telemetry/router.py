from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.common.dependencies import CurrentUser, DbSession, require_device_access, require_permission
from app.infrastructure.thingsboard.client import thingsboard_client
from app.modules.devices.repository import DeviceRepository
from app.modules.telemetry.schemas import TelemetryResponse

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get(
    "/devices/{device_id}/latest",
    response_model=TelemetryResponse,
    dependencies=[Depends(require_permission("telemetry:read")), Depends(require_device_access())],
)
async def latest_device_telemetry(
    device_id: str,
    db: DbSession,
    current_user: CurrentUser,
    keys: list[str] | None = Query(default=None),
) -> TelemetryResponse:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    values = await thingsboard_client.get_latest_telemetry(device.thingsboard_device_id, keys)
    return TelemetryResponse(
        device_id=device.id,
        values=values,
    )
