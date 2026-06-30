from fastapi import APIRouter, Depends

from app.common.dependencies import CurrentUser, DbSession, require_permission
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogRead], dependencies=[Depends(require_permission("audit:read"))])
def list_audit_logs(db: DbSession, _: CurrentUser) -> list[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
