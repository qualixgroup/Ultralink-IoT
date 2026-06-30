from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.modules.audit.service import AuditService
from app.modules.auth.schemas import TokenResponse
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            AuditService(self.users.db).record(
                "auth.login_failed",
                status="failed",
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"email": email},
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            AuditService(self.users.db).record(
                "auth.login_failed_inactive",
                status="failed",
                actor=user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={"email": email},
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        token = create_access_token(
            subject=user.id,
            extra_claims={
                "organization_id": user.organization_id,
                "partner_id": user.partner_id,
                "role": user.role,
            },
        )
        AuditService(self.users.db).record(
            "auth.login",
            actor=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"email": email},
        )
        return TokenResponse(access_token=token, user=UserRead.model_validate(user))
