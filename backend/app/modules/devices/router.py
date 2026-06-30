from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dependencies import (
    CurrentUser,
    DbSession,
    get_thingsboard_client,
    require_device_access,
    require_permission,
    visible_organization_ids,
)
from app.infrastructure.thingsboard.client import ThingsBoardClient
from app.modules.devices.models import Device
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate, DeviceRead, DeviceTelemetryRead, DeviceUpdate
from app.modules.devices.service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead], dependencies=[Depends(require_permission("devices:read"))])
def list_devices(db: DbSession, current_user: CurrentUser) -> list[Device]:
    return DeviceRepository(db).list(organization_ids=visible_organization_ids(db, current_user))


@router.post(
    "",
    response_model=DeviceRead,
    status_code=201,
    dependencies=[Depends(require_permission("devices:write"))],
)
async def create_device(
    payload: DeviceCreate,
    db: DbSession,
    current_user: CurrentUser,
    thingsboard: Annotated[ThingsBoardClient, Depends(get_thingsboard_client)],
) -> Device:
    try:
        return await DeviceService(db, thingsboard).create_device(payload, current_user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not create device through ThingsBoard",
        ) from exc


@router.get(
    "/{device_id}",
    response_model=DeviceRead,
    dependencies=[Depends(require_permission("devices:read")), Depends(require_device_access())],
)
def get_device(device_id: str, db: DbSession) -> Device:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.get(
    "/{device_id}/telemetry",
    response_model=DeviceTelemetryRead,
    dependencies=[Depends(require_permission("telemetry:read")), Depends(require_device_access())],
)
async def get_device_telemetry(
    device_id: str,
    db: DbSession,
    thingsboard: Annotated[ThingsBoardClient, Depends(get_thingsboard_client)],
) -> DeviceTelemetryRead:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return await DeviceService(db, thingsboard).get_telemetry(device)


@router.patch(
    "/{device_id}",
    response_model=DeviceRead,
    dependencies=[Depends(require_permission("devices:write")), Depends(require_device_access())],
)
def update_device(device_id: str, payload: DeviceUpdate, db: DbSession, current_user: CurrentUser) -> Device:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return DeviceService(db).update_device(device, payload, current_user)


@router.delete(
    "/{device_id}",
    response_model=DeviceRead,
    dependencies=[Depends(require_permission("devices:write")), Depends(require_device_access())],
)
async def delete_device(
    device_id: str,
    db: DbSession,
    current_user: CurrentUser,
    thingsboard: Annotated[ThingsBoardClient, Depends(get_thingsboard_client)],
) -> Device:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return await DeviceService(db, thingsboard).delete_device(device, current_user)
