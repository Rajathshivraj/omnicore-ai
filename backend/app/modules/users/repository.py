from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.modules.users.models import Role, User


class UserRepository(BaseRepository[User]):
    """Persistence boundary for user records."""

    model_class = User

    async def get_by_email(self, email: str, *, include_deleted: bool = False) -> User | None:
        statement = self.base_statement(include_deleted=include_deleted).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id_with_role(
        self,
        user_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> User | None:
        statement = (
            self.base_statement(include_deleted=include_deleted)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email_with_role(
        self,
        email: str,
        *,
        include_deleted: bool = False,
    ) -> User | None:
        statement = (
            self.base_statement(include_deleted=include_deleted)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        role_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[User]:
        statement = self.base_statement(include_deleted=include_deleted)
        if role_id:
            statement = statement.where(User.role_id == role_id)
        if status:
            statement = statement.where(User.status == status)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(User.email.ilike(pattern), User.full_name.ilike(pattern))
            )
        result = await self.session.execute(statement.offset(offset).limit(limit))
        return result.scalars().all()


class RoleRepository(BaseRepository[Role]):
    """Persistence boundary for role records."""

    model_class = Role

    async def get_by_slug(self, slug: str, *, include_deleted: bool = False) -> Role | None:
        statement = self.base_statement(include_deleted=include_deleted).where(Role.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Role]:
        statement = self.base_statement(include_deleted=include_deleted)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(or_(Role.name.ilike(pattern), Role.slug.ilike(pattern)))
        result = await self.session.execute(statement.order_by(Role.name).offset(offset).limit(limit))
        return result.scalars().all()
