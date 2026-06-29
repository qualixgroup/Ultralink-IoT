from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.common.dependencies import DbSession
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return AuthService(db).login(payload.email, payload.password)


@router.post("/token", response_model=TokenResponse)
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> TokenResponse:
    return AuthService(db).login(form_data.username, form_data.password)
