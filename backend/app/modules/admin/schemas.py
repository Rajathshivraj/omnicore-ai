from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.enums import UserStatus
from app.schemas.pagination import PaginatedResponse


class AdminUserUpdateRequest(BaseModel):
    role_id: UUID | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    status: UserStatus | None = None


class AdminRoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(min_length=1, max_length=80)
    description: str | None = None
    permissions: dict[str, object] = Field(default_factory=dict)
    is_system: bool = False


class AdminRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    permissions: dict[str, object]
    is_system: bool


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role_id: UUID
    email: EmailStr
    full_name: str
    phone: str | None
    status: str


class AdminOverviewResponse(BaseModel):
    status: str


AdminUserListResponse = PaginatedResponse[AdminUserResponse]
AdminRoleListResponse = PaginatedResponse[AdminRoleResponse]
