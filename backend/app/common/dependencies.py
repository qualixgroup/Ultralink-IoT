from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rbac import has_permission, is_platform_role
from app.core.security import decode_access_token
from app.infrastructure.database.session import get_db
from app.infrastructure.thingsboard.client import ThingsBoardClient, thingsboard_client
from app.modules.companies.models import Organization
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise credentials_error from exc

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_error

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise credentials_error
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


def get_thingsboard_client() -> ThingsBoardClient:
    return thingsboard_client


def require_role(*allowed_roles: str):
    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return dependency


def require_permission(permission: str):
    def dependency(current_user: CurrentUser) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")
        return current_user

    return dependency


def _request_value(request: Request, name: str) -> str | None:
    value = request.path_params.get(name)
    if value:
        return str(value)
    value = request.query_params.get(name)
    return str(value) if value else None


def user_can_access_partner(current_user: User, partner_id: str) -> bool:
    if is_platform_role(current_user.role):
        return True
    return bool(current_user.partner_id and current_user.partner_id == partner_id)


def user_can_access_organization(db: Session, current_user: User, organization_id: str) -> bool:
    if is_platform_role(current_user.role):
        return True

    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        return False

    if current_user.organization_id:
        return current_user.organization_id == organization.id
    if current_user.partner_id:
        return current_user.partner_id == organization.partner_id
    return False


def require_partner_access(partner_id_param: str = "partner_id"):
    def dependency(request: Request, current_user: CurrentUser) -> User:
        partner_id = _request_value(request, partner_id_param)
        if not partner_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing partner scope")
        if not user_can_access_partner(current_user, partner_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")
        return current_user

    return dependency


def require_organization_access(organization_id_param: str = "organization_id"):
    def dependency(request: Request, db: DbSession, current_user: CurrentUser) -> User:
        organization_id = _request_value(request, organization_id_param)
        if not organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing organization scope")
        if not user_can_access_organization(db, current_user, organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
        return current_user

    return dependency


def visible_organization_ids(db: Session, current_user: User) -> list[str] | None:
    if is_platform_role(current_user.role):
        return None
    if current_user.organization_id:
        return [current_user.organization_id]
    if current_user.partner_id:
        rows = db.query(Organization.id).filter(Organization.partner_id == current_user.partner_id).all()
        return [row[0] for row in rows]
    return []
