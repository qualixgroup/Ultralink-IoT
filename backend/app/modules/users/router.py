from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dependencies import CurrentUser, DbSession, require_permission, visible_organization_ids
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_permission("users:read"))])
def list_users(db: DbSession, current_user: CurrentUser) -> list[User]:
    organization_ids = visible_organization_ids(db, current_user)
    partner_id = None if current_user.role.startswith("platform_") else current_user.partner_id
    return UserRepository(db).list(partner_id=partner_id, organization_ids=organization_ids)


@router.post("", response_model=UserRead, status_code=201, dependencies=[Depends(require_permission("users:write"))])
def create_user(payload: UserCreate, db: DbSession, current_user: CurrentUser) -> User:
    return UserService(db).create_user(payload, current_user)


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("users:write"))])
def update_user(user_id: str, payload: UserUpdate, db: DbSession, current_user: CurrentUser) -> User:
    target = UserRepository(db).get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserService(db).update_user(target, payload, current_user)


@router.delete("/{user_id}", response_model=UserRead, dependencies=[Depends(require_permission("users:write"))])
def delete_user(user_id: str, db: DbSession, current_user: CurrentUser) -> User:
    target = UserRepository(db).get_by_id(user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserService(db).deactivate_user(target, current_user)
