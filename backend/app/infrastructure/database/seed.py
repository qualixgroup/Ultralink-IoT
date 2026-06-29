from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.security import hash_password
from app.infrastructure.database.session import SessionLocal
from app.modules.companies.models import Company
from app.modules.users.models import User


def ensure_default_admin() -> None:
    if settings.app_env == "production":
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.first_superuser_email).first()
        if existing:
            return

        company = Company(name="Ultralink", document="00000000000000", status="active")
        db.add(company)
        db.flush()

        db.add(
            User(
                company_id=company.id,
                email=settings.first_superuser_email,
                full_name=settings.first_superuser_name,
                hashed_password=hash_password(settings.first_superuser_password),
                role="owner",
                is_active=True,
            )
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()
