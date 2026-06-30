from conftest import auth_headers
from sqlalchemy.orm import Session

from app.modules.devices.models import Device


def test_partner_crud_as_platform_owner(client, tenant_data):
    owner = tenant_data["platform_owner"]

    created = client.post(
        "/api/v1/partners",
        headers=auth_headers(owner),
        json={"name": "Partner Sprint"},
    )
    assert created.status_code == 201, created.text
    partner_id = created.json()["id"]

    fetched = client.get(f"/api/v1/partners/{partner_id}", headers=auth_headers(owner))
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Partner Sprint"

    updated = client.patch(
        f"/api/v1/partners/{partner_id}",
        headers=auth_headers(owner),
        json={"name": "Partner Sprint 2"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Partner Sprint 2"

    deleted = client.delete(f"/api/v1/partners/{partner_id}", headers=auth_headers(owner))
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"


def test_organization_crud_as_partner_admin(client, tenant_data):
    partner_admin = tenant_data["partner_admin"]
    partner_a = tenant_data["partner_a"]

    created = client.post(
        "/api/v1/organizations",
        headers=auth_headers(partner_admin),
        json={"partner_id": partner_a.id, "name": "Org Sprint", "document": "999"},
    )
    assert created.status_code == 201, created.text
    organization_id = created.json()["id"]

    fetched = client.get(f"/api/v1/organizations/{organization_id}", headers=auth_headers(partner_admin))
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/organizations/{organization_id}",
        headers=auth_headers(partner_admin),
        json={"name": "Org Sprint 2"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Org Sprint 2"

    deleted = client.delete(f"/api/v1/organizations/{organization_id}", headers=auth_headers(partner_admin))
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"


def test_site_crud_as_organization_admin(client, tenant_data):
    admin = tenant_data["org_admin"]
    org_a = tenant_data["org_a"]

    created = client.post(
        "/api/v1/sites",
        headers=auth_headers(admin),
        json={"organization_id": org_a.id, "name": "Site Sprint", "address": "Rua A"},
    )
    assert created.status_code == 201, created.text
    site_id = created.json()["id"]

    fetched = client.get(f"/api/v1/sites/{site_id}", headers=auth_headers(admin))
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/sites/{site_id}",
        headers=auth_headers(admin),
        json={"name": "Site Sprint 2"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Site Sprint 2"

    deleted = client.delete(f"/api/v1/sites/{site_id}", headers=auth_headers(admin))
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"


def test_asset_crud_as_organization_admin(client, tenant_data):
    admin = tenant_data["org_admin"]
    org_a = tenant_data["org_a"]
    site_a = tenant_data["site_a"]

    created = client.post(
        "/api/v1/assets",
        headers=auth_headers(admin),
        json={"organization_id": org_a.id, "site_id": site_a.id, "name": "Asset Sprint", "type": "generator"},
    )
    assert created.status_code == 201, created.text
    asset_id = created.json()["id"]

    fetched = client.get(f"/api/v1/assets/{asset_id}", headers=auth_headers(admin))
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/assets/{asset_id}",
        headers=auth_headers(admin),
        json={"name": "Asset Sprint 2"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Asset Sprint 2"

    deleted = client.delete(f"/api/v1/assets/{asset_id}", headers=auth_headers(admin))
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"


def test_device_crud_syncs_with_thingsboard(client, db_session: Session, tenant_data, use_fake_thingsboard):
    admin = tenant_data["org_admin"]
    org_a = tenant_data["org_a"]
    asset_a = tenant_data["asset_a"]

    created = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin),
        json={"organization_id": org_a.id, "asset_id": asset_a.id, "name": "Device Sprint", "type": "sensor"},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    device_id = body["id"]
    assert body["status"] == "offline"
    assert "thingsboard_device_id" not in body
    assert use_fake_thingsboard.created == ["Device Sprint"]

    stored = db_session.query(Device).filter(Device.id == device_id).one()
    assert stored.thingsboard_device_id == "tb-device-sprint"

    fetched = client.get(f"/api/v1/devices/{device_id}", headers=auth_headers(admin))
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Device Sprint"

    updated = client.patch(
        f"/api/v1/devices/{device_id}",
        headers=auth_headers(admin),
        json={"label": "Principal"},
    )
    assert updated.status_code == 200
    assert updated.json()["label"] == "Principal"

    deleted = client.delete(f"/api/v1/devices/{device_id}", headers=auth_headers(admin))
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"
    assert use_fake_thingsboard.deleted == ["tb-device-sprint"]


def test_device_telemetry_endpoint(client, db_session: Session, tenant_data, use_fake_thingsboard):
    admin = tenant_data["org_admin"]
    org_a = tenant_data["org_a"]
    asset_a = tenant_data["asset_a"]

    created = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin),
        json={"organization_id": org_a.id, "asset_id": asset_a.id, "name": "Telemetry Sprint", "type": "sensor"},
    )
    assert created.status_code == 201, created.text
    device_id = created.json()["id"]

    response = client.get(f"/api/v1/devices/{device_id}/telemetry", headers=auth_headers(admin))

    assert response.status_code == 200
    body = response.json()
    assert body["device_id"] == device_id
    assert body["temperatura"] == 24.5
    assert body["bateria"] == 88.0
    assert body["combustivel"] == 62.0
    assert body["rssi"] == -67
    assert body["source"] == "thingsboard"


def test_partner_admin_cannot_read_other_partner_resource(client, tenant_data):
    partner_admin = tenant_data["partner_admin"]
    org_c = tenant_data["org_c"]

    response = client.get(f"/api/v1/organizations/{org_c.id}", headers=auth_headers(partner_admin))

    assert response.status_code == 403
