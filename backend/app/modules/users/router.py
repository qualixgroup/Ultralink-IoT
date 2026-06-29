from fastapi import APIRouter

from app.common.dependencies import CurrentUser, DbSession
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser) -> UserRead:
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(db: DbSession, _: CurrentUser) -> list[UserRead]:
    return UserRepository(db).list()


@router.post("", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: DbSession, _: CurrentUser) -> UserRead:
    return UserService(db).create_user(payload)
