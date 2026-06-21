from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.modules.inventory.models import Inventory, InventoryMovement
from app.modules.products.models import Product


class InventoryRepository(BaseRepository[Inventory]):
    """Persistence boundary for inventory records."""

    model_class = Inventory

    async def get_by_product_location(
        self,
        *,
        product_id: UUID,
        location_code: str = "default",
        include_deleted: bool = False,
        for_update: bool = False,
    ) -> Inventory | None:
        statement = self.base_statement(include_deleted=include_deleted).where(
            Inventory.product_id == product_id,
            Inventory.location_code == location_code,
        )
        if for_update:
            statement = statement.with_for_update()
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        status: str | None = None,
        location_code: str | None = None,
        low_stock_only: bool = False,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Inventory]:
        statement = self.base_statement(include_deleted=include_deleted)
        if search:
            statement = statement.join(Product)
        if status:
            statement = statement.where(Inventory.inventory_status == status)
        if location_code:
            statement = statement.where(Inventory.location_code == location_code)
        if low_stock_only:
            statement = statement.where(Inventory.stock_available <= Inventory.reorder_point)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
            )
        result = await self.session.execute(
            statement.order_by(Inventory.inventory_status, Inventory.location_code)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()


class InventoryMovementRepository(BaseRepository[InventoryMovement]):
    """Persistence boundary for stock movement audit records."""

    model_class = InventoryMovement
