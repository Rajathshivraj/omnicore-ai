from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.modules.products.models import Category, Product


class ProductRepository(BaseRepository[Product]):
    """Persistence boundary for products and categories."""

    model_class = Product

    async def get_by_sku(self, sku: str, *, include_deleted: bool = False) -> Product | None:
        statement = self.base_statement(include_deleted=include_deleted).where(Product.sku == sku)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str, *, include_deleted: bool = False) -> Product | None:
        statement = self.base_statement(include_deleted=include_deleted).where(Product.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        category_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Product]:
        statement = self.base_statement(include_deleted=include_deleted)
        if category_id:
            statement = statement.where(Product.category_id == category_id)
        if status:
            statement = statement.where(Product.status == status)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Product.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                    Product.slug.ilike(pattern),
                )
            )
        result = await self.session.execute(
            statement.order_by(Product.name).offset(offset).limit(limit)
        )
        return result.scalars().all()


class CategoryRepository(BaseRepository[Category]):
    """Persistence boundary for product categories."""

    model_class = Category

    async def get_by_slug(self, slug: str, *, include_deleted: bool = False) -> Category | None:
        statement = self.base_statement(include_deleted=include_deleted).where(Category.slug == slug)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        parent_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Category]:
        statement = self.base_statement(include_deleted=include_deleted)
        if parent_id:
            statement = statement.where(Category.parent_id == parent_id)
        if status:
            statement = statement.where(Category.status == status)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(Category.name.ilike(pattern), Category.slug.ilike(pattern))
            )
        result = await self.session.execute(
            statement.order_by(Category.sort_order, Category.name).offset(offset).limit(limit)
        )
        return result.scalars().all()
