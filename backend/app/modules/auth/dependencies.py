from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.dependencies import DbSession
from app.core.errors import AuthorizationError
from app.core.security import oauth2_scheme
from app.modules.auth.service import AuthService
from app.modules.shared.permissions import Permission, ROLE_PERMISSIONS, RoleSlug
from app.modules.users.models import User
from app.modules.users.repository import RoleRepository, UserRepository

AccessToken = Annotated[str, Depends(oauth2_scheme)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_auth_service(session: DbSession, settings: SettingsDep) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        role_repository=RoleRepository(session),
        settings=settings,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: AccessToken,
    auth_service: AuthServiceDep,
) -> User:
    return await auth_service.get_current_user(access_token=token)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: RoleSlug) -> Callable[[User], Awaitable[User]]:
    allowed_role_values = {role.value for role in allowed_roles}

    async def dependency(current_user: CurrentUser) -> User:
        role_slug = current_user.role.slug if current_user.role else None
        if role_slug == RoleSlug.ADMIN.value or role_slug in allowed_role_values:
            return current_user
        raise AuthorizationError()

    return dependency


def require_permissions(*required_permissions: Permission) -> Callable[[User], Awaitable[User]]:
    required_permission_values = set(required_permissions)
    required_permission_strings = {permission.value for permission in required_permissions}

    async def dependency(current_user: CurrentUser) -> User:
        role_slug = current_user.role.slug if current_user.role else None
        if not role_slug:
            raise AuthorizationError()

        role_permissions = current_user.role.permissions if current_user.role else {}
        configured_permissions = set(role_permissions.get("permissions", []))
        if Permission.FULL_ACCESS.value in configured_permissions:
            return current_user
        if required_permission_strings.issubset(configured_permissions):
            return current_user

        try:
            role = RoleSlug(role_slug)
        except ValueError as exc:
            raise AuthorizationError() from exc

        granted_permissions = ROLE_PERMISSIONS.get(role, set())
        if Permission.FULL_ACCESS in granted_permissions:
            return current_user
        if required_permission_values.issubset(granted_permissions):
            return current_user
        raise AuthorizationError()

    return dependency


CustomerUser = Annotated[User, Depends(require_roles(RoleSlug.CUSTOMER))]
InventoryManagerUser = Annotated[User, Depends(require_roles(RoleSlug.INVENTORY_MANAGER))]
WarehouseManagerUser = Annotated[User, Depends(require_roles(RoleSlug.WAREHOUSE_MANAGER))]
AdminUser = Annotated[User, Depends(require_roles(RoleSlug.ADMIN))]
