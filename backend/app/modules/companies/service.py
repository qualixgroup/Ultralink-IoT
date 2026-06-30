from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import user_can_access_organization
from app.modules.audit.service import AuditService
from app.modules.companies.models import Asset, Site
from app.modules.companies.repository import AssetRepository, SiteRepository
from app.modules.companies.schemas import AssetCreate, SiteCreate
from app.modules.users.models import User


class CompanyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sites = SiteRepository(db)
        self.assets = AssetRepository(db)

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
