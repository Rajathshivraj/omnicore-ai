from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.db.enums import FulfillmentStatus, OrderStatus
from app.modules.orders.service import OrderService


class FakeOrderRepository:
    def __init__(self, order) -> None:
        self.order = order

    async def get_by_id_with_items(self, order_id):
        return self.order if self.order.id == order_id else None

    async def update(self, order, data: dict):
        for key, value in data.items():
            setattr(order, key, value)
        return order


class FakeProductRepository:
    pass


class FakeInventoryService:
    def __init__(self) -> None:
        self.released: list[tuple] = []

    async def release_reserved_stock(self, *, product_id, quantity, location_code="default"):
        self.released.append((product_id, quantity, location_code))


@pytest.mark.asyncio
async def test_cancel_order_releases_reserved_stock_for_each_line() -> None:
    product_id = uuid4()
    order = SimpleNamespace(
        id=uuid4(),
        status=OrderStatus.PENDING,
        fulfillment_status=FulfillmentStatus.READY_TO_PICK,
        items=[SimpleNamespace(product_id=product_id, quantity=2)],
        placed_at=datetime.now(UTC),
    )
    inventory = FakeInventoryService()
    service = OrderService(
        order_repository=FakeOrderRepository(order),
        product_repository=FakeProductRepository(),
        inventory_service=inventory,
    )

    updated = await service.update_status(order_id=order.id, status=OrderStatus.CANCELLED)

    assert updated.status == OrderStatus.CANCELLED
    assert inventory.released == [(product_id, 2, "default")]
    assert updated.cancelled_at is not None
