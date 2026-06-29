from fastapi import APIRouter

from app.common.dependencies import CurrentUser, DbSession
from app.modules.alerts.models import Alert
from app.modules.alerts.schemas import AlertCreate, AlertRead

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(db: DbSession, _: CurrentUser) -> list[AlertRead]:
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.post("", response_model=AlertRead, status_code=201)
def create_alert(payload: AlertCreate, db: DbSession, _: CurrentUser) -> AlertRead:
    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
