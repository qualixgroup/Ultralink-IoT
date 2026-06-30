from typing import cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import user_can_access_organization, user_can_access_partner
from app.core.rbac import PLATFORM_ROLES
from app.core.security import hash_password
from app.modules.audit.service import AuditService
from app.modules.companies.models import Organization
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import RoleName, UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def create_user(self, payload: UserCreate, actor: User) -> User:
        if self.repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        self._validate_scope(payload, actor)

        user = User(
            partner_id=payload.partner_id,
            organization_id=payload.organization_id,
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        created = self.repository.create(user)
        AuditService(self.repository.db).record(
            "user.created",
            actor=actor,
            partner_id=created.partner_id,
            organization_id=created.organization_id,
            resource_type="user",
            resource_id=created.id,
            metadata={"email": created.email, "role": created.role},
        )
        return created

    def _validate_scope(self, payload: UserCreate, actor: User) -> None:
        if payload.role in PLATFORM_ROLES:
            if actor.role != "platform_owner":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create platform users")
            return

        if payload.organization_id:
            organization = (
                self.repository.db.query(Organization).filter(Organization.id == payload.organization_id).first()
            )
            if not organization:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
            if not payload.partner_id:
                payload.partner_id = organization.partner_id
            if payload.partner_id != organization.partner_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant scope")
            if not user_can_access_organization(self.repository.db, actor, organization.id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
            return

        if payload.partner_id:
            if actor.organization_id and not actor.role.startswith("platform_"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner-level users are not allowed")
            if not user_can_access_partner(actor, payload.partner_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")
            return

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User tenant scope is required")

    def update_user(self, target: User, payload: UserUpdate, actor: User) -> User:
        requested = UserCreate(
            partner_id=payload.partner_id if payload.partner_id is not None else target.partner_id,
            organization_id=payload.organization_id if payload.organization_id is not None else target.organization_id,
            email=target.email,
            full_name=payload.full_name or target.full_name,
            password="not-used",
            role=cast(RoleName, payload.role or target.role),
        )
        self._validate_scope(requested, actor)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(target, field, value)
        self.repository.db.commit()
        self.repository.db.refresh(target)
        AuditService(self.repository.db).record(
            "user.updated",
            actor=actor,
            partner_id=target.partner_id,
            organization_id=target.organization_id,
            resource_type="user",
            resource_id=target.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return target

    def deactivate_user(self, target: User, actor: User) -> User:
        requested = UserCreate(
            partner_id=target.partner_id,
            organization_id=target.organization_id,
            email=target.email,
            full_name=target.full_name,
            password="not-used",
            role=cast(RoleName, target.role),
        )
        self._validate_scope(requested, actor)
        target.is_active = False
        self.repository.db.commit()
        self.repository.db.refresh(target)
        AuditService(self.repository.db).record(
            "user.deleted",
            actor=actor,
            partner_id=target.partner_id,
            organization_id=target.organization_id,
            resource_type="user",
            resource_id=target.id,
        )
        return target
