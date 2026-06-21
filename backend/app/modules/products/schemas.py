from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import ProductStatus
from app.schemas.pagination import PaginatedResponse


class CategoryCreateRequest(BaseModel):
    parent_id: UUID | None = None
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    description: str | None = None
    sort_order: int = 0
    status: ProductStatus = ProductStatus.ACTIVE


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_id: UUID | None
    name: str
    slug: str
    description: str | None
    sort_order: int
    status: str


class ProductCreateRequest(BaseModel):
    category_id: UUID
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=240)
    description: str | None = None
    status: ProductStatus = ProductStatus.ACTIVE
    price_amount: Decimal = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    cost_amount: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = None
    attributes: dict[str, object] = Field(default_factory=dict)


class ProductUpdateRequest(BaseModel):
    category_id: UUID | None = None
    sku: str | None = Field(default=None, min_length=1, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = None
    status: ProductStatus | None = None
    price_amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    cost_amount: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = None
    attributes: dict[str, object] | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    sku: str
    name: str
    slug: str
    description: str | None
    status: str
    price_amount: Decimal
    currency: str
    cost_amount: Decimal | None
    image_url: str | None
    attributes: dict[str, object]


ProductListResponse = PaginatedResponse[ProductResponse]
CategoryListResponse = PaginatedResponse[CategoryResponse]
