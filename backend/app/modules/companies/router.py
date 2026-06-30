from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dependencies import (
    CurrentUser,
    DbSession,
    require_permission,
    user_can_access_partner,
    visible_organization_ids,
)
from app.modules.audit.service import AuditService
from app.modules.companies.models import Organization, Partner
from app.modules.companies.repository import OrganizationRepository, PartnerRepository
from app.modules.companies.schemas import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    PartnerCreate,
    PartnerRead,
)

router = APIRouter(tags=["organizations"])


@router.get("/partners", response_model=list[PartnerRead], dependencies=[Depends(require_permission("partners:read"))])
def list_partners(db: DbSession, current_user: CurrentUser) -> list[Partner]:
    if current_user.role.startswith("platform_"):
        return PartnerRepository(db).list()
    if not current_user.partner_id:
        return []
    partner = PartnerRepository(db).get_by_id(current_user.partner_id)
    return [partner] if partner else []


@router.post(
    "/partners",
    response_model=PartnerRead,
    status_code=201,
    dependencies=[Depends(require_permission("partners:write"))],
)
def create_partner(payload: PartnerCreate, db: DbSession, current_user: CurrentUser) -> Partner:
    partner = PartnerRepository(db).create(payload)
    AuditService(db).record(
        "partner.created",
        actor=current_user,
        partner_id=partner.id,
        resource_type="partner",
        resource_id=partner.id,
        metadata={"name": partner.name},
    )
    return partner


@router.get(
    "/organizations",
    response_model=list[OrganizationRead],
    dependencies=[Depends(require_permission("organizations:read"))],
)
@router.get(
    "/companies",
    response_model=list[OrganizationRead],
    dependencies=[Depends(require_permission("organizations:read"))],
)
def list_organizations(db: DbSession, current_user: CurrentUser) -> list[Organization]:
    repository = OrganizationRepository(db)
    organization_ids = visible_organization_ids(db, current_user)
    if organization_ids is None:
        return repository.list()
    if current_user.organization_id:
        return repository.list(organization_id=current_user.organization_id)
    if current_user.partner_id:
        return repository.list(partner_id=current_user.partner_id)
    return []


@router.post(
    "/organizations",
    response_model=OrganizationRead,
    status_code=201,
    dependencies=[Depends(require_permission("organizations:write"))],
)
@router.post(
    "/companies",
    response_model=OrganizationRead,
    status_code=201,
    dependencies=[Depends(require_permission("organizations:write"))],
)
def create_organization(payload: OrganizationCreate, db: DbSession, current_user: CurrentUser) -> Organization:
    if not user_can_access_partner(current_user, payload.partner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")
    organization = OrganizationRepository(db).create(payload)
    AuditService(db).record(
        "organization.created",
        actor=current_user,
        partner_id=organization.partner_id,
        organization_id=organization.id,
        resource_type="organization",
        resource_id=organization.id,
        metadata={"name": organization.name},
    )
    return organization


@router.patch(
    "/organizations/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(require_permission("organizations:write"))],
)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Organization:
    repository = OrganizationRepository(db)
    organization = repository.get_by_id(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if not user_can_access_partner(current_user, organization.partner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")

    updated = repository.update(organization, payload)
    AuditService(db).record(
        "organization.updated",
        actor=current_user,
        partner_id=updated.partner_id,
        organization_id=updated.id,
        resource_type="organization",
        resource_id=updated.id,
        metadata=payload.model_dump(exclude_unset=True),
    )
    return updated


@router.delete(
    "/organizations/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(require_permission("organizations:write"))],
)
def delete_organization(organization_id: str, db: DbSession, current_user: CurrentUser) -> Organization:
    repository = OrganizationRepository(db)
    organization = repository.get_by_id(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if not user_can_access_partner(current_user, organization.partner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")

    updated = repository.update(organization, OrganizationUpdate(status="deleted"))
    AuditService(db).record(
        "organization.deleted",
        actor=current_user,
        partner_id=updated.partner_id,
        organization_id=updated.id,
        resource_type="organization",
        resource_id=updated.id,
    )
    return updated
