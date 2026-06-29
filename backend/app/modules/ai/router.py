from fastapi import APIRouter

from app.common.dependencies import CurrentUser

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
def ai_status(_: CurrentUser) -> dict[str, str]:
    return {"status": "planned", "provider": "openai"}
