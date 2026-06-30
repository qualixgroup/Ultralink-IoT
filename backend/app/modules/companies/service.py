from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import user_can_access_organization, user_can_access_partner
from app.modules.audit.service import AuditService
from app.modules.companies.models import Asset, Organization, Partner, Site
from app.modules.companies.repository import AssetRepository, OrganizationRepository, PartnerRepository, SiteRepository
from app.modules.companies.schemas import (
    AssetCreate,
    AssetUpdate,
    OrganizationCreate,
    OrganizationUpdate,
    PartnerCreate,
    PartnerUpdate,
    SiteCreate,
    SiteUpdate,
)
from app.modules.users.models import User


class CompanyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.partners = PartnerRepository(db)
        self.organizations = OrganizationRepository(db)
        self.sites = SiteRepository(db)
        self.assets = AssetRepository(db)

    def create_partner(self, payload: PartnerCreate, actor: User) -> Partner:
        partner = self.partners.create(payload)
        AuditService(self.db).record(
            "partner.created",
            actor=actor,
            partner_id=partner.id,
            resource_type="partner",
            resource_id=partner.id,
            metadata={"name": partner.name},
        )
        return partner

    def update_partner(self, partner: Partner, payload: PartnerUpdate, actor: User) -> Partner:
        if not user_can_access_partner(actor, partner.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")

        updated = self.partners.update(partner, payload)
        AuditService(self.db).record(
            "partner.updated",
            actor=actor,
            partner_id=updated.id,
            resource_type="partner",
            resource_id=updated.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return updated

    def create_organization(self, payload: OrganizationCreate, actor: User) -> Organization:
        if not user_can_access_partner(actor, payload.partner_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")

        organization = self.organizations.create(payload)
        AuditService(self.db).record(
            "organization.created",
            actor=actor,
            partner_id=organization.partner_id,
            organization_id=organization.id,
            resource_type="organization",
            resource_id=organization.id,
            metadata={"name": organization.name},
        )
        return organization

    def update_organization(self, organization: Organization, payload: OrganizationUpdate, actor: User) -> Organization:
        if not user_can_access_partner(actor, organization.partner_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")

        updated = self.organizations.update(organization, payload)
        AuditService(self.db).record(
            "organization.updated",
            actor=actor,
            partner_id=updated.partner_id,
            organization_id=updated.id,
            resource_type="organization",
            resource_id=updated.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return updated

    def create_site(self, payload: SiteCreate, actor: User) -> Site:
        if not user_can_access_organization(self.db, actor, payload.organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        site = self.sites.create(payload)
        AuditService(self.db).record(
            "site.created",
            actor=actor,
            organization_id=site.organization_id,
            resource_type="site",
            resource_id=site.id,
            metadata={"name": site.name},
        )
        return site

    def update_site(self, site: Site, payload: SiteUpdate, actor: User) -> Site:
        if not user_can_access_organization(self.db, actor, site.organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        updated = self.sites.update(site, payload)
        AuditService(self.db).record(
            "site.updated",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="site",
            resource_id=updated.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return updated

    def create_asset(self, payload: AssetCreate, actor: User) -> Asset:
        if not user_can_access_organization(self.db, actor, payload.organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        site = self.sites.get_by_id(payload.site_id)
        if not site or site.organization_id != payload.organization_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site scope")

        asset = self.assets.create(payload)
        AuditService(self.db).record(
            "asset.created",
            actor=actor,
            organization_id=asset.organization_id,
            resource_type="asset",
            resource_id=asset.id,
            metadata={"name": asset.name, "type": asset.type},
        )
        return asset

    def update_asset(self, asset: Asset, payload: AssetUpdate, actor: User) -> Asset:
        if not user_can_access_organization(self.db, actor, asset.organization_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")

        if payload.site_id:
            site = self.sites.get_by_id(payload.site_id)
            if not site or site.organization_id != asset.organization_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid site scope")

        updated = self.assets.update(asset, payload)
        AuditService(self.db).record(
            "asset.updated",
            actor=actor,
            organization_id=updated.organization_id,
            resource_type="asset",
            resource_id=updated.id,
            metadata=payload.model_dump(exclude_unset=True),
        )
        return updated
