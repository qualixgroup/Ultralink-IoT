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


def test_organization_isolation_on_device_listing(client, db_session: Session, tenant_data):
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    admin_a = tenant_data["org_admin"]
    make_device(db_session, org_a.id, "Sensor A", "tb-a")
    make_device(db_session, org_b.id, "Sensor B", "tb-b")

    response = client.get("/api/v1/devices", headers=auth_headers(admin_a))

    assert response.status_code == 200
    names = {device["name"] for device in response.json()}
    assert names == {"Sensor A"}


def test_device_creation_does_not_cross_tenants_or_expose_thingsboard(
    client,
    db_session: Session,
    tenant_data,
    use_fake_thingsboard,
):
    org_a = tenant_data["org_a"]
    org_b = tenant_data["org_b"]
    admin_a = tenant_data["org_admin"]
    admin_b = tenant_data["org_b_admin"]

    denied = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin_a),
        json={"organization_id": org_b.id, "name": "Cross Tenant Sensor", "type": "sensor"},
    )
    assert denied.status_code == 403

    created = client.post(
        "/api/v1/devices",
        headers=auth_headers(admin_a),
        json={"organization_id": org_a.id, "name": "Tenant Sensor", "type": "sensor"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["organization_id"] == org_a.id
    assert "thingsboard_device_id" not in body

    assert db_session.query(Device).filter(Device.organization_id == org_b.id).count() == 0

    other_tenant_list = client.get("/api/v1/devices", headers=auth_headers(admin_b))
    assert other_tenant_list.status_code == 200
    assert other_tenant_list.json() == []
