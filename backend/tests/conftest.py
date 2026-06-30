import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "false"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-enough-entropy-123456"

from app.common.dependencies import get_thingsboard_client  # noqa: E402
from app.core.rate_limit import reset_login_rate_limits  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.infrastructure.database import models  # noqa: F401, E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.companies.models import Organization, Partner  # noqa: E402
from app.modules.devices.models import Device  # noqa: E402
from app.modules.users.models import User  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    reset_login_rate_limits()
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def tenant_data(db_session: Session) -> dict[str, object]:
    partner_a = Partner(name="Partner A")
    partner_b = Partner(name="Partner B")
    db_session.add_all([partner_a, partner_b])
    db_session.flush()

    org_a = Organization(partner_id=partner_a.id, name="Org A", document="111")
    org_b = Organization(partner_id=partner_a.id, name="Org B", document="222")
    org_c = Organization(partner_id=partner_b.id, name="Org C", document="333")
    db_session.add_all([org_a, org_b, org_c])
    db_session.flush()

    platform_owner = make_user(db_session, "owner@ultralink.io", "platform_owner")
    partner_admin = make_user(db_session, "partner@ultralink.io", "partner_admin", partner_id=partner_a.id)
    org_admin = make_user(
        db_session,
        "admin-a@ultralink.io",
        "organization_admin",
        partner_id=partner_a.id,
        organization_id=org_a.id,
    )
    org_operator = make_user(
        db_session,
        "operator-a@ultralink.io",
        "organization_operator",
        partner_id=partner_a.id,
        organization_id=org_a.id,
    )
    org_b_admin = make_user(
        db_session,
        "admin-b@ultralink.io",
        "organization_admin",
        partner_id=partner_a.id,
        organization_id=org_b.id,
    )
    inactive = make_user(
        db_session,
        "inactive@ultralink.io",
        "organization_admin",
        partner_id=partner_a.id,
        organization_id=org_a.id,
        is_active=False,
    )
    db_session.commit()

    return {
        "partner_a": partner_a,
        "partner_b": partner_b,
        "org_a": org_a,
        "org_b": org_b,
        "org_c": org_c,
        "platform_owner": platform_owner,
        "partner_admin": partner_admin,
        "org_admin": org_admin,
        "org_operator": org_operator,
        "org_b_admin": org_b_admin,
        "inactive": inactive,
    }


def make_user(
    db: Session,
    email: str,
    role: str,
    *,
    partner_id: str | None = None,
    organization_id: str | None = None,
    password: str = "secret123",
    is_active: bool = True,
) -> User:
    user = User(
        partner_id=partner_id,
        organization_id=organization_id,
        email=email,
        full_name=email.split("@")[0],
        hashed_password=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    return user


def make_device(db: Session, organization_id: str, name: str, tb_id: str) -> Device:
    device = Device(
        organization_id=organization_id,
        thingsboard_device_id=tb_id,
        name=name,
        type="sensor",
        status="online",
        attributes={},
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(
        user.id,
        {
            "partner_id": user.partner_id,
            "organization_id": user.organization_id,
            "role": user.role,
        },
    )
    return {"Authorization": f"Bearer {token}"}


class FakeThingsBoardClient:
    async def create_device(self, name: str, device_type: str, label: str | None = None) -> dict:
        return {"id": {"id": f"tb-{name.lower().replace(' ', '-')}"}}


@pytest.fixture()
def fake_thingsboard() -> FakeThingsBoardClient:
    return FakeThingsBoardClient()


@pytest.fixture()
def use_fake_thingsboard(fake_thingsboard: FakeThingsBoardClient) -> FakeThingsBoardClient:
    app.dependency_overrides[get_thingsboard_client] = lambda: fake_thingsboard
    return fake_thingsboard
