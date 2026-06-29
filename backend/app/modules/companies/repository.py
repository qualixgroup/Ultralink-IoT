from sqlalchemy.orm import Session

from app.modules.companies.models import Company
from app.modules.companies.schemas import CompanyCreate


class CompanyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Company]:
        return self.db.query(Company).order_by(Company.created_at.desc()).all()

    def create(self, payload: CompanyCreate) -> Company:
        company = Company(**payload.model_dump())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
