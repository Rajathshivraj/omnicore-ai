from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.core.errors import NotFoundError
from app.modules.users.models import Role, User
from app.modules.users.repository import RoleRepository, UserRepository


class AdminService:
    """Coordinates administrative user and role management workflows."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def list_users(
        self,
        *,
        role_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[User]:
        return await self.user_repository.list_filtered(
            role_id=role_id,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    async def update_user(self, user_id: UUID, data: dict[str, Any]) -> User:
        if "role_id" in data and data["role_id"] is not None:
            role = await self.role_repository.get_by_id(data["role_id"])
            if role is None:
                raise NotFoundError("Role not found.")
        user = await self.get_user(user_id)
        if not data:
            return user
        return await self.user_repository.update(user, data)

    async def list_roles(
        self,
        *,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Role]:
        return await self.role_repository.list_filtered(
            search=search,
            offset=offset,
            limit=limit,
        )

    async def create_role(self, data: dict[str, Any]) -> Role:
        return await self.role_repository.create(data)
