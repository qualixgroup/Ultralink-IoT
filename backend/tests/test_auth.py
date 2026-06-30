from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog


def test_valid_login(client, db_session: Session, tenant_data):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-a@ultralink.io", "password": "secret123"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["user"]["role"] == "organization_admin"
    assert body["user"]["organization_id"] == tenant_data["org_a"].id

    audit = db_session.query(AuditLog).filter(AuditLog.action == "auth.login").one()
    assert audit.event_data == {"email": "admin-a@ultralink.io"}


def test_invalid_login_records_failure_without_password(client, db_session: Session, tenant_data):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-a@ultralink.io", "password": "wrong"},
    )

    assert response.status_code == 401, response.text
    audit = db_session.query(AuditLog).filter(AuditLog.action == "auth.login_failed").one()
    assert "password" not in audit.event_data
    assert audit.event_data["email"] == "admin-a@ultralink.io"


def test_inactive_user_cannot_login(client, db_session: Session, tenant_data):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@ultralink.io", "password": "secret123"},
    )

    assert response.status_code == 403, response.text
    audit = db_session.query(AuditLog).filter(AuditLog.action == "auth.login_failed_inactive").one()
    assert audit.status == "failed"
