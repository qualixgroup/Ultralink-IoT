from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PartnerCreate(BaseModel):
    name: str


class PartnerUpdate(BaseModel):
    name: str | None = None
    status: str | None = None


class PartnerRead(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationCreate(BaseModel):
    partner_id: str
    name: str
    document: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    document: str | None = None
    status: str | None = None


class OrganizationRead(BaseModel):
    id: str
    partner_id: str
    name: str
    document: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteCreate(BaseModel):
    organization_id: str
    name: str
    address: str | None = None


class SiteUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    status: str | None = None


class SiteRead(BaseModel):
    id: str
    organization_id: str
    name: str
    address: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetCreate(BaseModel):
    organization_id: str
    site_id: str
    name: str
    type: str = "generic"


class AssetUpdate(BaseModel):
    site_id: str | None = None
    name: str | None = None
    type: str | None = None
    status: str | None = None


class AssetRead(BaseModel):
    id: str
    organization_id: str
    site_id: str
    name: str
    type: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
