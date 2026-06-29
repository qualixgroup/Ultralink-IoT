from fastapi import APIRouter, HTTPException, status

from app.common.dependencies import CurrentUser
from app.infrastructure.thingsboard.client import thingsboard_client

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/thingsboard/status")
async def thingsboard_status(_: CurrentUser) -> dict[str, str]:
    try:
        return await thingsboard_client.health()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ThingsBoard unavailable") from exc


@router.get("/whatsapp/status")
def whatsapp_status(_: CurrentUser) -> dict[str, str]:
    return {"status": "planned", "provider": "whatsapp"}
