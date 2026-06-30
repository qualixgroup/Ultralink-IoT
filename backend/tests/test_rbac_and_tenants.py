from conftest import auth_headers, make_device
from sqlalchemy.orm import Session

from app.modules.devices.models import Device


def test_access_denied_by_role(client, tenant_data):
    operator = tenant_data["org_operator"]
    org_a = tenant_data["org_a"]

    response = client.post(
        "/api/v1/users",
        headers=auth_headers(operator),
        json={
            "partner_id": org_a.partner_id,
            "organization_id": org_a.id,
            "email": "new@ultralink.io",
            "full_name": "New User",
            "password": "secret123",
            "role": "organization_operator",
        },
    )

    assert response.status_code == 403


def test_partner_a_does_not_see_partner_b_organization(client, tenant_data):
    partner_admin = tenant_data["partner_admin"]
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    org_c = tenant_data["org_c"]

    response = client.get("/api/v1/organizations", headers=auth_headers(partner_admin))

    assert response.status_code == 200
    organization_ids = {organization["id"] for organization in response.json()}
    assert organization_ids == {org_a.id, org_b.id}
    assert org_c.id not in organization_ids


def test_organization_isolation_on_device_listing(client, db_session: Session, tenant_data):
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    asset_a = tenant_data["asset_a"]
    asset_b = tenant_data["asset_b"]
    admin_a = tenant_data["org_admin"]
    make_device(db_session, org_a.id, "Sensor A", "tb-a", asset_id=asset_a.id)
    make_device(db_session, org_b.id, "Sensor B", "tb-b", asset_id=asset_b.id)

    response = client.get("/api/v1/devices", headers=auth_headers(admin_a))

    assert response.status_code == 200
    names = {device["name"] for device in response.json()}
    assert names == {"Sensor A"}


def test_read_only_cannot_create_device(client, tenant_data, use_fake_thingsboard):
    org_a = tenant_data["org_a"]
    asset_a = tenant_data["asset_a"]
    read_only = tenant_data["read_only"]

    response = client.post(
        "/api/v1/devices",
        headers=auth_headers(read_only),
        json={"organization_id": org_a.id, "asset_id": asset_a.id, "name": "Read Only Sensor", "type": "sensor"},
    )

    assert response.status_code == 403


def test_device_creation_does_not_cross_tenants_or_expose_thingsboard(
    client,
    db_session: Session,
    tenant_data,
    use_fake_thingsboard,
):
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    asset_a = tenant_data["asset_a"]
    asset_b = tenant_data["asset_b"]
    admin_a = tenant_data["org_admin"]
    admin_b = tenant_data["org_b_admin"]

    denied = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin_a),
        json={"organization_id": org_b.id, "asset_id": asset_b.id, "name": "Cross Tenant Sensor", "type": "sensor"},
    )
    assert denied.status_code == 403

    invalid_asset = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin_a),
        json={"organization_id": org_a.id, "asset_id": asset_b.id, "name": "Wrong Asset Sensor", "type": "sensor"},
    )
    assert invalid_asset.status_code == 400

    created = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin_a),
        json={"organization_id": org_a.id, "asset_id": asset_a.id, "name": "Tenant Sensor", "type": "sensor"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["organization_id"] == org_a.id
    assert "thingsboard_device_id" not in body

    assert db_session.query(Device).filter(Device.organization_id == org_b.id).count() == 0

    other_tenant_list = client.get("/api/v1/devices", headers=auth_headers(admin_b))
    assert other_tenant_list.status_code == 200
    assert other_tenant_list.json() == []


def test_platform_owner_lists_all_devices(client, db_session: Session, tenant_data):
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    org_c = tenant_data["org_c"]
    asset_a = tenant_data["asset_a"]
    asset_b = tenant_data["asset_b"]
    asset_c = tenant_data["asset_c"]
    platform_owner = tenant_data["platform_owner"]
    make_device(db_session, org_a.id, "Sensor A", "tb-platform-a", asset_id=asset_a.id)
    make_device(db_session, org_b.id, "Sensor B", "tb-platform-b", asset_id=asset_b.id)
    make_device(db_session, org_c.id, "Sensor C", "tb-platform-c", asset_id=asset_c.id)

    response = client.get("/api/v1/devices", headers=auth_headers(platform_owner))

    assert response.status_code == 200
    names = {device["name"] for device in response.json()}
    assert names == {"Sensor A", "Sensor B", "Sensor C"}
