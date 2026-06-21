from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.core.errors import BusinessRuleError, NotFoundError
from app.db.enums import InventoryStatus
from app.modules.inventory.models import Inventory
from app.modules.inventory.repository import InventoryMovementRepository, InventoryRepository


class InventoryService:
    """Coordinates stock position, inventory health, and adjustment workflows."""

    def __init__(
        self,
        inventory_repository: InventoryRepository,
        movement_repository: InventoryMovementRepository | None = None,
    ) -> None:
        self.inventory_repository = inventory_repository
        self.movement_repository = movement_repository

    async def get_inventory(self, inventory_id: UUID) -> Inventory:
        inventory = await self.inventory_repository.get_by_id(inventory_id)
        if inventory is None:
            raise NotFoundError("Inventory record not found.")
        return inventory

    async def list_inventory(
        self,
        *,
        status: str | None = None,
        location_code: str | None = None,
        low_stock_only: bool = False,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Inventory]:
        return await self.inventory_repository.list_filtered(
            status=status,
            location_code=location_code,
            low_stock_only=low_stock_only,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def create_inventory(self, data: dict[str, Any]) -> Inventory:
        stock_on_hand = int(data.get("stock_on_hand", 0))
        stock_reserved = int(data.get("stock_reserved", 0))
        requested_available = data.get("stock_available")
        stock_available = (
            stock_on_hand - stock_reserved
            if requested_available is None
            else int(requested_available)
        )
        if stock_reserved > stock_on_hand:
            raise BusinessRuleError("Reserved stock cannot exceed stock on hand.")
        if stock_available != stock_on_hand - stock_reserved:
            raise BusinessRuleError(
                "Available stock must equal stock on hand minus reserved stock."
            )
        data["stock_available"] = stock_available
        data["inventory_status"] = self._derive_inventory_status_from_values(
            stock_available=stock_available,
            reorder_point=int(data.get("reorder_point", 0)),
        )
        return await self.inventory_repository.create(data)

    async def update_inventory(self, inventory_id: UUID, data: dict[str, Any]) -> Inventory:
        inventory = await self.get_inventory(inventory_id)
        if not data:
            return inventory
        return await self.inventory_repository.update(inventory, data)

    async def get_by_product_location(
        self,
        *,
        product_id: UUID,
        location_code: str = "default",
    ) -> Inventory:
        inventory = await self.inventory_repository.get_by_product_location(
            product_id=product_id,
            location_code=location_code,
        )
        if inventory is None:
            raise NotFoundError("Inventory record not found for product and location.")
        return inventory

    async def adjust_stock(
        self,
        *,
        inventory_id: UUID,
        quantity_delta: int,
        reason: str | None = None,
    ) -> Inventory:
        inventory = await self.get_inventory(inventory_id)
        next_on_hand = inventory.stock_on_hand + quantity_delta
        if next_on_hand < 0:
            raise BusinessRuleError("Inventory adjustment cannot create negative stock.")
        if inventory.stock_reserved > next_on_hand:
            raise BusinessRuleError(
                "Inventory adjustment cannot reduce stock below reserved quantity."
            )

        inventory.stock_on_hand = next_on_hand
        inventory.stock_available = next_on_hand - inventory.stock_reserved
        inventory.inventory_status = self._derive_inventory_status(inventory)
        updated = await self.inventory_repository.update(
            inventory,
            {
                "stock_on_hand": inventory.stock_on_hand,
                "stock_available": inventory.stock_available,
                "inventory_status": inventory.inventory_status,
            },
        )
        await self._record_movement(
            inventory=updated,
            quantity_delta=quantity_delta,
            movement_type="adjustment",
            reason=reason,
        )
        return updated

    async def reserve_stock(
        self,
        *,
        product_id: UUID,
        quantity: int,
        location_code: str = "default",
    ) -> Inventory:
        if quantity <= 0:
            raise BusinessRuleError("Reserved quantity must be greater than zero.")

        inventory = await self.inventory_repository.get_by_product_location(
            product_id=product_id,
            location_code=location_code,
            for_update=True,
        )
        if inventory is None:
            raise NotFoundError("Inventory record not found for product and location.")
        if inventory.stock_available < quantity:
            raise BusinessRuleError("Insufficient available stock to reserve.")

        inventory.stock_reserved += quantity
        inventory.stock_available -= quantity
        inventory.inventory_status = self._derive_inventory_status(inventory)
        updated = await self.inventory_repository.update(
            inventory,
            {
                "stock_reserved": inventory.stock_reserved,
                "stock_available": inventory.stock_available,
                "inventory_status": inventory.inventory_status,
            },
        )
        await self._record_movement(
            inventory=updated,
            quantity_delta=-quantity,
            movement_type="reservation",
            reason="Reserved for customer order",
        )
        return updated

    async def release_reserved_stock(
        self,
        *,
        product_id: UUID,
        quantity: int,
        location_code: str = "default",
    ) -> Inventory:
        if quantity <= 0:
            raise BusinessRuleError("Release quantity must be greater than zero.")

        inventory = await self.inventory_repository.get_by_product_location(
            product_id=product_id,
            location_code=location_code,
            for_update=True,
        )
        if inventory is None:
            raise NotFoundError("Inventory record not found for product and location.")
        if inventory.stock_reserved < quantity:
            raise BusinessRuleError("Cannot release more stock than is currently reserved.")

        inventory.stock_reserved -= quantity
        inventory.stock_available += quantity
        inventory.inventory_status = self._derive_inventory_status(inventory)
        updated = await self.inventory_repository.update(
            inventory,
            {
                "stock_reserved": inventory.stock_reserved,
                "stock_available": inventory.stock_available,
                "inventory_status": inventory.inventory_status,
            },
        )
        await self._record_movement(
            inventory=updated,
            quantity_delta=quantity,
            movement_type="reservation_release",
            reason="Released after order cancellation",
        )
        return updated

    def _derive_inventory_status(self, inventory: Inventory) -> InventoryStatus:
        return self._derive_inventory_status_from_values(
            stock_available=inventory.stock_available,
            reorder_point=inventory.reorder_point,
        )

    def _derive_inventory_status_from_values(
        self,
        *,
        stock_available: int,
        reorder_point: int,
    ) -> InventoryStatus:
        if stock_available == 0:
            return InventoryStatus.OUT_OF_STOCK
        if stock_available <= max(1, reorder_point // 2):
            return InventoryStatus.STOCKOUT_RISK
        if stock_available <= reorder_point:
            return InventoryStatus.LOW_STOCK
        return InventoryStatus.HEALTHY

    async def _record_movement(
        self,
        *,
        inventory: Inventory,
        quantity_delta: int,
        movement_type: str,
        reason: str | None = None,
    ) -> None:
        if self.movement_repository is None:
            return
        await self.movement_repository.create(
            {
                "inventory_id": inventory.id,
                "product_id": inventory.product_id,
                "movement_type": movement_type,
                "quantity_delta": quantity_delta,
                "reason": reason,
            }
        )
