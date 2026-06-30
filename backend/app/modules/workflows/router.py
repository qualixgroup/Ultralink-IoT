from fastapi import APIRouter, Depends

from app.common.dependencies import CurrentUser, require_permission

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", dependencies=[Depends(require_permission("workflows:read"))])
def list_workflows(_: CurrentUser) -> list[dict[str, str]]:
    return []
