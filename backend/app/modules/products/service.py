from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.core.errors import NotFoundError
from app.modules.products.models import Category, Product
from app.modules.products.repository import CategoryRepository, ProductRepository


class ProductService:
    """Coordinates product catalog and category workflows."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.product_repository = product_repository
        self.category_repository = category_repository

    async def create_product(self, data: dict[str, Any]) -> Product:
        category = await self.category_repository.get_by_id(data["category_id"])
        if category is None:
            raise NotFoundError("Category not found.")
        return await self.product_repository.create(data)

    async def get_product(self, product_id: UUID) -> Product:
        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found.")
        return product

    async def list_products(
        self,
        *,
        category_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Product]:
        return await self.product_repository.list_filtered(
            category_id=category_id,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def update_product(self, product_id: UUID, data: dict[str, Any]) -> Product:
        product = await self.get_product(product_id)
        if "category_id" in data and data["category_id"] is not None:
            category = await self.category_repository.get_by_id(data["category_id"])
            if category is None:
                raise NotFoundError("Category not found.")
        return await self.product_repository.update(product, data)

    async def archive_product(self, product_id: UUID, *, deleted_by_id: UUID | None = None) -> Product:
        product = await self.get_product(product_id)
        return await self.product_repository.soft_delete(product, deleted_by_id=deleted_by_id)

    async def create_category(self, data: dict[str, Any]) -> Category:
        return await self.category_repository.create(data)

    async def list_categories(
        self,
        *,
        parent_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Category]:
        return await self.category_repository.list_filtered(
            parent_id=parent_id,
            status=status,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def get_category(self, category_id: UUID) -> Category:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise NotFoundError("Category not found.")
        return category
