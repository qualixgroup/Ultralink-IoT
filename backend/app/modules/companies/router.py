from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dependencies import (
    CurrentUser,
    DbSession,
    require_permission,
    user_can_access_organization,
    user_can_access_partner,
    visible_organization_ids,
)
from app.modules.companies.models import Asset, Organization, Partner, Site
from app.modules.companies.repository import AssetRepository, OrganizationRepository, PartnerRepository, SiteRepository
from app.modules.companies.schemas import (
    AssetCreate,
    AssetRead,
    AssetUpdate,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    PartnerCreate,
    PartnerRead,
    PartnerUpdate,
    SiteCreate,
    SiteRead,
    SiteUpdate,
)
from app.modules.companies.service import CompanyService

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
    return CompanyService(db).create_partner(payload, current_user)


@router.get(
    "/partners/{partner_id}",
    response_model=PartnerRead,
    dependencies=[Depends(require_permission("partners:read"))],
)
def get_partner(partner_id: str, db: DbSession, current_user: CurrentUser) -> Partner:
    partner = PartnerRepository(db).get_by_id(partner_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    if not user_can_access_partner(current_user, partner.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")
    return partner


@router.patch(
    "/partners/{partner_id}",
    response_model=PartnerRead,
    dependencies=[Depends(require_permission("partners:write"))],
)
def update_partner(
    partner_id: str,
    payload: PartnerUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Partner:
    partner = PartnerRepository(db).get_by_id(partner_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return CompanyService(db).update_partner(partner, payload, current_user)


@router.delete(
    "/partners/{partner_id}",
    response_model=PartnerRead,
    dependencies=[Depends(require_permission("partners:write"))],
)
def delete_partner(partner_id: str, db: DbSession, current_user: CurrentUser) -> Partner:
    partner = PartnerRepository(db).get_by_id(partner_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return CompanyService(db).update_partner(partner, PartnerUpdate(status="deleted"), current_user)


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
    return CompanyService(db).create_organization(payload, current_user)


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(require_permission("organizations:read"))],
)
def get_organization(organization_id: str, db: DbSession, current_user: CurrentUser) -> Organization:
    organization = OrganizationRepository(db).get_by_id(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if not user_can_access_organization(db, current_user, organization.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
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
    return CompanyService(db).update_organization(organization, payload, current_user)


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
    return CompanyService(db).update_organization(organization, OrganizationUpdate(status="deleted"), current_user)


@router.get("/sites", response_model=list[SiteRead], dependencies=[Depends(require_permission("sites:read"))])
def list_sites(db: DbSession, current_user: CurrentUser) -> list[Site]:
    return SiteRepository(db).list(organization_ids=visible_organization_ids(db, current_user))


@router.post(
    "/sites",
    response_model=SiteRead,
    status_code=201,
    dependencies=[Depends(require_permission("sites:write"))],
)
def create_site(payload: SiteCreate, db: DbSession, current_user: CurrentUser) -> Site:
    return CompanyService(db).create_site(payload, current_user)


@router.get("/sites/{site_id}", response_model=SiteRead, dependencies=[Depends(require_permission("sites:read"))])
def get_site(site_id: str, db: DbSession, current_user: CurrentUser) -> Site:
    site = SiteRepository(db).get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    if not user_can_access_organization(db, current_user, site.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    return site


@router.patch("/sites/{site_id}", response_model=SiteRead, dependencies=[Depends(require_permission("sites:write"))])
def update_site(site_id: str, payload: SiteUpdate, db: DbSession, current_user: CurrentUser) -> Site:
    site = SiteRepository(db).get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return CompanyService(db).update_site(site, payload, current_user)


@router.delete("/sites/{site_id}", response_model=SiteRead, dependencies=[Depends(require_permission("sites:write"))])
def delete_site(site_id: str, db: DbSession, current_user: CurrentUser) -> Site:
    site = SiteRepository(db).get_by_id(site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return CompanyService(db).update_site(site, SiteUpdate(status="deleted"), current_user)


@router.get("/assets", response_model=list[AssetRead], dependencies=[Depends(require_permission("assets:read"))])
def list_assets(db: DbSession, current_user: CurrentUser) -> list[Asset]:
    return AssetRepository(db).list(organization_ids=visible_organization_ids(db, current_user))


@router.post(
    "/assets",
    response_model=AssetRead,
    status_code=201,
    dependencies=[Depends(require_permission("assets:write"))],
)
def create_asset(payload: AssetCreate, db: DbSession, current_user: CurrentUser) -> Asset:
    return CompanyService(db).create_asset(payload, current_user)


@router.get("/assets/{asset_id}", response_model=AssetRead, dependencies=[Depends(require_permission("assets:read"))])
def get_asset(asset_id: str, db: DbSession, current_user: CurrentUser) -> Asset:
    asset = AssetRepository(db).get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if not user_can_access_organization(db, current_user, asset.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    return asset


@router.patch(
    "/assets/{asset_id}",
    response_model=AssetRead,
    dependencies=[Depends(require_permission("assets:write"))],
)
def update_asset(asset_id: str, payload: AssetUpdate, db: DbSession, current_user: CurrentUser) -> Asset:
    asset = AssetRepository(db).get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return CompanyService(db).update_asset(asset, payload, current_user)


@router.delete(
    "/assets/{asset_id}",
    response_model=AssetRead,
    dependencies=[Depends(require_permission("assets:write"))],
)
def delete_asset(asset_id: str, db: DbSession, current_user: CurrentUser) -> Asset:
    asset = AssetRepository(db).get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return CompanyService(db).update_asset(asset, AssetUpdate(status="deleted"), current_user)
