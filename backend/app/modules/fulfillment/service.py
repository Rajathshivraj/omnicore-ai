from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.errors import BusinessRuleError, NotFoundError
from app.db.enums import FulfillmentStatus, OrderStatus
from app.modules.fulfillment.models import FulfillmentRecord
from app.modules.fulfillment.repository import FulfillmentRepository
from app.modules.orders.repository import OrderRepository


class FulfillmentService:
    """Coordinates warehouse fulfillment queue records."""

    ALLOWED_TRANSITIONS: dict[FulfillmentStatus, set[FulfillmentStatus]] = {
        FulfillmentStatus.READY_TO_PICK: {FulfillmentStatus.PICKING, FulfillmentStatus.EXCEPTION},
        FulfillmentStatus.PICKING: {FulfillmentStatus.PACKED, FulfillmentStatus.EXCEPTION},
        FulfillmentStatus.PACKED: {FulfillmentStatus.SHIPPED, FulfillmentStatus.EXCEPTION},
        FulfillmentStatus.SHIPPED: set(),
        FulfillmentStatus.EXCEPTION: {FulfillmentStatus.READY_TO_PICK},
    }

    def __init__(
        self,
        *,
        fulfillment_repository: FulfillmentRepository,
        order_repository: OrderRepository,
    ) -> None:
        self.fulfillment_repository = fulfillment_repository
        self.order_repository = order_repository

    async def create_record(self, data: dict[str, Any]) -> FulfillmentRecord:
        order = await self.order_repository.get_by_id_with_items(data["order_id"])
        if order is None:
            raise NotFoundError("Order not found for fulfillment.")
        if OrderStatus(order.status) == OrderStatus.CANCELLED:
            raise BusinessRuleError("Cancelled orders cannot enter fulfillment.")
        return await self.fulfillment_repository.create(
            {
                "order_id": order.id,
                "warehouse_code": data.get("warehouse_code", "default"),
                "status": FulfillmentStatus.READY_TO_PICK,
            }
        )

    async def list_records(
        self,
        *,
        status: str | None = None,
        warehouse_code: str | None = None,
        order_id: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[FulfillmentRecord]:
        return await self.fulfillment_repository.list_filtered(
            status=status,
            warehouse_code=warehouse_code,
            order_id=order_id,
            offset=offset,
            limit=limit,
        )

    async def get_record(self, record_id: UUID) -> FulfillmentRecord:
        record = await self.fulfillment_repository.get_by_id(record_id)
        if record is None:
            raise NotFoundError("Fulfillment record not found.")
        return record

    async def update_record(
        self,
        *,
        record_id: UUID,
        status: FulfillmentStatus,
        tracking_reference: str | None = None,
        exception_reason: str | None = None,
    ) -> FulfillmentRecord:
        record = await self.get_record(record_id)
        current_status = FulfillmentStatus(record.status)
        if status not in self.ALLOWED_TRANSITIONS[current_status]:
            raise BusinessRuleError("Invalid fulfillment status transition.")

        update_data: dict[str, Any] = {
            "status": status,
            "tracking_reference": tracking_reference,
            "exception_reason": exception_reason,
        }
        if status == FulfillmentStatus.SHIPPED:
            update_data["completed_at"] = datetime.now(UTC)
        return await self.fulfillment_repository.update(record, update_data)
