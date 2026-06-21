from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import BusinessRuleError
from app.db.enums import InventoryStatus
from app.modules.inventory.service import InventoryService


class FakeInventoryRepository:
    def __init__(self, inventory=None) -> None:
        self.inventory = inventory

    async def get_by_id(self, inventory_id):
        return self.inventory if self.inventory and self.inventory.id == inventory_id else None

    async def get_by_product_location(self, **_: object):
        return self.inventory

    async def create(self, data: dict):
        self.inventory = SimpleNamespace(id=uuid4(), **data)
        return self.inventory

    async def update(self, inventory, data: dict):
        for key, value in data.items():
            setattr(inventory, key, value)
        return inventory


class FakeMovementRepository:
    def __init__(self) -> None:
        self.created: list[dict] = []

    async def create(self, data: dict):
        self.created.append(data)
        return SimpleNamespace(id=uuid4(), **data)


@pytest.mark.asyncio
async def test_create_inventory_validates_available_stock_formula() -> None:
    service = InventoryService(inventory_repository=FakeInventoryRepository())

    with pytest.raises(BusinessRuleError):
        await service.create_inventory(
            {
                "product_id": uuid4(),
                "stock_on_hand": 10,
                "stock_reserved": 2,
                "stock_available": 10,
                "reorder_point": 5,
            }
        )


@pytest.mark.asyncio
async def test_release_reserved_stock_restores_available_and_logs_movement() -> None:
    product_id = uuid4()
    inventory = SimpleNamespace(
        id=uuid4(),
        product_id=product_id,
        stock_on_hand=10,
        stock_reserved=4,
        stock_available=6,
        reorder_point=2,
        inventory_status=InventoryStatus.HEALTHY,
    )
    movements = FakeMovementRepository()
    service = InventoryService(
        inventory_repository=FakeInventoryRepository(inventory),
        movement_repository=movements,
    )

    updated = await service.release_reserved_stock(product_id=product_id, quantity=3)

    assert updated.stock_reserved == 1
    assert updated.stock_available == 9
    assert movements.created[0]["movement_type"] == "reservation_release"
