from fastapi import APIRouter, HTTPException, status

from app.common.dependencies import CurrentUser, DbSession
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schemas import DeviceCreate, DeviceRead
from app.modules.devices.service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead])
def list_devices(db: DbSession, current_user: CurrentUser) -> list[DeviceRead]:
    company_id = None if current_user.role == "owner" else current_user.company_id
    return DeviceRepository(db).list(company_id=company_id)


@router.post("", response_model=DeviceRead, status_code=201)
async def create_device(payload: DeviceCreate, db: DbSession, _: CurrentUser) -> DeviceRead:
    try:
        return await DeviceService(db).create_device(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not create device through ThingsBoard",
        ) from exc
