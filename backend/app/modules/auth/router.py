from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.common.dependencies import DbSession
from app.core.rate_limit import check_login_rate_limit, clear_login_rate_limit
from app.modules.audit.service import AuditService
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession, request: Request) -> TokenResponse:
    identifier = f"{_client_ip(request)}:{payload.email.lower()}"
    try:
        check_login_rate_limit(identifier)
    except HTTPException:
        AuditService(db).record(
            "security.login_rate_limited",
            status="blocked",
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            metadata={"email": payload.email},
        )
        raise
    response = AuthService(db).login(
        payload.email,
        payload.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    clear_login_rate_limit(identifier)
    return response


@router.post("/token", response_model=TokenResponse)
def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
    request: Request,
) -> TokenResponse:
    identifier = f"{_client_ip(request)}:{form_data.username.lower()}"
    try:
        check_login_rate_limit(identifier)
    except HTTPException:
        AuditService(db).record(
            "security.login_rate_limited",
            status="blocked",
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            metadata={"email": form_data.username},
        )
        raise
    response = AuthService(db).login(
        form_data.username,
        form_data.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    clear_login_rate_limit(identifier)
    return response
