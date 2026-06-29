from fastapi import APIRouter

from app.common.dependencies import CurrentUser

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("")
def list_workflows(_: CurrentUser) -> list[dict[str, str]]:
    return []
