from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession
from app.modules.admin.schemas import (
    AdminOverviewResponse,
    AdminRoleCreateRequest,
    AdminRoleListResponse,
    AdminRoleResponse,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.modules.admin.service import AdminService
from app.modules.auth.dependencies import require_permissions
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.modules.users.repository import RoleRepository, UserRepository
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_admin_service(session: DbSession) -> AdminService:
    return AdminService(
        user_repository=UserRepository(session),
        role_repository=RoleRepository(session),
    )


AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


@router.get(
    "/overview",
    response_model=AdminOverviewResponse,
    summary="Get admin overview",
    description="Lightweight admin module health endpoint.",
)
async def get_admin_overview(
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
) -> AdminOverviewResponse:
    return AdminOverviewResponse(status="ok")


@router.get(
    "/users",
    response_model=AdminUserListResponse,
    summary="List users",
    description="Returns paginated users with role, status, and search filters.",
)
async def list_users(
    service: AdminServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
    role_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> AdminUserListResponse:
    items = await service.list_users(
        role_id=role_id,
        status=status,
        search=search,
        offset=offset,
        limit=limit,
    )
    return AdminUserListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.get("/users/{user_id}", response_model=AdminUserResponse, summary="Get user")
async def get_user(
    user_id: UUID,
    service: AdminServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
) -> object:
    return await service.get_user(user_id)


@router.patch("/users/{user_id}", response_model=AdminUserResponse, summary="Update user")
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    service: AdminServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
) -> object:
    user = await service.update_user(user_id, payload.model_dump(exclude_unset=True))
    await session.commit()
    return user


@router.get(
    "/roles",
    response_model=AdminRoleListResponse,
    summary="List roles",
    description="Returns paginated role records.",
)
async def list_roles(
    service: AdminServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> AdminRoleListResponse:
    items = await service.list_roles(search=search, offset=offset, limit=limit)
    return AdminRoleListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.post("/roles", response_model=AdminRoleResponse, status_code=201, summary="Create role")
async def create_role(
    payload: AdminRoleCreateRequest,
    service: AdminServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_USERS))],
) -> object:
    role = await service.create_role(payload.model_dump())
    await session.commit()
    return role
