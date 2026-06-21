from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.core.errors import ConflictError
from app.modules.auth.service import AuthService
from app.modules.shared.permissions import RoleSlug


class FakeUserRepository:
    def __init__(self) -> None:
        self.user = None

    async def get_by_email(self, email: str):
        return self.user if self.user and self.user.email == email else None

    async def get_by_email_with_role(self, email: str):
        return self.user if self.user and self.user.email == email else None

    async def get_by_id_with_role(self, user_id):
        return self.user if self.user and self.user.id == user_id else None

    async def create(self, data: dict):
        self.user = SimpleNamespace(id=uuid4(), role=SimpleNamespace(slug="customer"), **data)
        return self.user


class FakeRoleRepository:
    async def get_by_slug(self, slug: str):
        if slug == RoleSlug.CUSTOMER.value:
            return SimpleNamespace(id=uuid4(), slug=slug)
        return None


@pytest.mark.asyncio
async def test_register_customer_hashes_password_and_assigns_role() -> None:
    users = FakeUserRepository()
    service = AuthService(
        user_repository=users,
        role_repository=FakeRoleRepository(),
        settings=Settings(),
    )

    user = await service.register_customer(
        email="NEW@EXAMPLE.COM",
        password="Password123!",
        full_name="New User",
    )

    assert user.email == "new@example.com"
    assert user.password_hash != "Password123!"
    assert user.role.slug == "customer"


@pytest.mark.asyncio
async def test_register_customer_rejects_duplicate_email() -> None:
    users = FakeUserRepository()
    users.user = SimpleNamespace(email="taken@example.com")
    service = AuthService(
        user_repository=users,
        role_repository=FakeRoleRepository(),
        settings=Settings(),
    )

    with pytest.raises(ConflictError):
        await service.register_customer(
            email="taken@example.com",
            password="Password123!",
            full_name="Taken User",
        )
