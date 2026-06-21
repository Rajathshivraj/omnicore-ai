from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession
from app.modules.auth.dependencies import require_permissions
from app.modules.products.repository import CategoryRepository, ProductRepository
from app.modules.products.schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from app.modules.products.service import ProductService
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/products", tags=["products"])


async def get_product_service(session: DbSession) -> ProductService:
    return ProductService(
        product_repository=ProductRepository(session),
        category_repository=CategoryRepository(session),
    )


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="Returns paginated product catalog records with optional category, status, and text filters.",
)
async def list_products(
    service: ProductServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_PRODUCTS))],
    category_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ProductListResponse:
    items = await service.list_products(
        category_id=category_id,
        status=status,
        search=search,
        offset=offset,
        limit=limit,
    )
    return ProductListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
    summary="Create product",
    description="Creates a product catalog record. Requires product management permission.",
)
async def create_product(
    payload: ProductCreateRequest,
    service: ProductServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_PRODUCTS))],
) -> object:
    product = await service.create_product(payload.model_dump())
    await session.commit()
    return product


@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="List categories",
    description="Returns paginated product categories.",
)
async def list_categories(
    service: ProductServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_PRODUCTS))],
    parent_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> CategoryListResponse:
    items = await service.list_categories(
        parent_id=parent_id,
        status=status,
        search=search,
        offset=offset,
        limit=limit,
    )
    return CategoryListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=201,
    summary="Create category",
    description="Creates a product category. Requires product management permission.",
)
async def create_category(
    payload: CategoryCreateRequest,
    service: ProductServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_PRODUCTS))],
) -> object:
    category = await service.create_category(payload.model_dump())
    await session.commit()
    return category


@router.get("/categories/{category_id}", response_model=CategoryResponse, summary="Get category")
async def get_category(
    category_id: UUID,
    service: ProductServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_PRODUCTS))],
) -> object:
    return await service.get_category(category_id)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product")
async def get_product(
    product_id: UUID,
    service: ProductServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_PRODUCTS))],
) -> object:
    return await service.get_product(product_id)


@router.patch("/{product_id}", response_model=ProductResponse, summary="Update product")
async def update_product(
    product_id: UUID,
    payload: ProductUpdateRequest,
    service: ProductServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_PRODUCTS))],
) -> object:
    product = await service.update_product(
        product_id,
        payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    return product


@router.delete("/{product_id}", response_model=ProductResponse, summary="Archive product")
async def archive_product(
    product_id: UUID,
    service: ProductServiceDep,
    session: DbSession,
    current_user: Annotated[User, Depends(require_permissions(Permission.MANAGE_PRODUCTS))],
) -> object:
    product = await service.archive_product(product_id, deleted_by_id=current_user.id)
    await session.commit()
    return product
