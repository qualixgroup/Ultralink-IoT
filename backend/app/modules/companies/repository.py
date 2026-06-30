from sqlalchemy.orm import Session

from app.modules.companies.models import Asset, Organization, Partner, Site
from app.modules.companies.schemas import AssetCreate, OrganizationCreate, OrganizationUpdate, PartnerCreate, SiteCreate


class PartnerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, partner_id: str) -> Partner | None:
        return self.db.query(Partner).filter(Partner.id == partner_id).first()

    def list(self) -> list[Partner]:
        return self.db.query(Partner).order_by(Partner.created_at.desc()).all()

    def create(self, payload: PartnerCreate) -> Partner:
        partner = Partner(**payload.model_dump())
        self.db.add(partner)
        self.db.commit()
        self.db.refresh(partner)
        return partner


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, organization_id: str) -> Organization | None:
        return self.db.query(Organization).filter(Organization.id == organization_id).first()

    def list(self, partner_id: str | None = None, organization_id: str | None = None) -> list[Organization]:
        query = self.db.query(Organization)
        if partner_id:
            query = query.filter(Organization.partner_id == partner_id)
        if organization_id:
            query = query.filter(Organization.id == organization_id)
        return query.order_by(Organization.created_at.desc()).all()

    def create(self, payload: OrganizationCreate) -> Organization:
        organization = Organization(**payload.model_dump())
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def update(self, organization: Organization, payload: OrganizationUpdate) -> Organization:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(organization, field, value)
        self.db.commit()
        self.db.refresh(organization)
        return organization


class SiteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, site_id: str) -> Site | None:
        return self.db.query(Site).filter(Site.id == site_id).first()

    def create(self, payload: SiteCreate) -> Site:
        site = Site(**payload.model_dump())
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site


class AssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, asset_id: str) -> Asset | None:
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def create(self, payload: AssetCreate) -> Asset:
        asset = Asset(**payload.model_dump())
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset
