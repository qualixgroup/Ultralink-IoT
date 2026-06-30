from sqlalchemy.orm import Session

from app.modules.users.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def list(
        self,
        partner_id: str | None = None,
        organization_ids: list[str] | None = None,
    ) -> list[User]:
        query = self.db.query(User)
        if partner_id:
            query = query.filter(User.partner_id == partner_id)
        if organization_ids is not None:
            query = query.filter(User.organization_id.in_(organization_ids))
        return query.order_by(User.created_at.desc()).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
