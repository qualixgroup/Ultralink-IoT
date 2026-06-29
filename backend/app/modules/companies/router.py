from fastapi import APIRouter

from app.common.dependencies import CurrentUser, DbSession
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.schemas import CompanyCreate, CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
def list_companies(db: DbSession, _: CurrentUser) -> list[CompanyRead]:
    return CompanyRepository(db).list()


@router.post("", response_model=CompanyRead, status_code=201)
def create_company(payload: CompanyCreate, db: DbSession, _: CurrentUser) -> CompanyRead:
    return CompanyRepository(db).create(payload)
