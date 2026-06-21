from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.core.errors import BusinessRuleError, NotFoundError
from app.db.enums import FulfillmentStatus, OrderStatus, PaymentStatus
from app.modules.inventory.service import InventoryService
from app.modules.orders.models import Order, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository


class OrderService:
    """Coordinates order creation, totals, stock reservation, and lifecycle workflows."""

    ALLOWED_STATUS_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
        OrderStatus.PROCESSING: {OrderStatus.FULFILLED, OrderStatus.CANCELLED},
        OrderStatus.FULFILLED: set(),
        OrderStatus.CANCELLED: set(),
    }

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        inventory_service: InventoryService,
    ) -> None:
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.inventory_service = inventory_service

    async def get_order(self, order_id: UUID) -> Order:
        order = await self.order_repository.get_by_id_with_items(order_id)
        if order is None:
            raise NotFoundError("Order not found.")
        return order

    async def get_customer_order(self, *, order_id: UUID, customer_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if order.customer_id != customer_id:
            raise NotFoundError("Order not found.")
        return order

    async def list_orders(
        self,
        *,
        customer_id: UUID | None = None,
        status: str | None = None,
        fulfillment_status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Order]:
        return await self.order_repository.list_filtered(
            customer_id=customer_id,
            status=status,
            fulfillment_status=fulfillment_status,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def create_order(
        self,
        *,
        customer_id: UUID,
        items: Sequence[dict[str, object]],
        tax_amount: Decimal = Decimal("0.00"),
        shipping_amount: Decimal = Decimal("0.00"),
        discount_amount: Decimal = Decimal("0.00"),
        currency: str = "USD",
        shipping_name: str | None = None,
        shipping_address: dict[str, object] | None = None,
    ) -> Order:
        if not items:
            raise BusinessRuleError("Order must contain at least one item.")

        order_items: list[OrderItem] = []
        subtotal = Decimal("0.00")

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            if not isinstance(product_id, UUID):
                raise BusinessRuleError("Order item product_id must be a UUID.")
            if not isinstance(quantity, int) or quantity <= 0:
                raise BusinessRuleError("Order item quantity must be greater than zero.")

            product = await self.product_repository.get_by_id(product_id)
            if product is None:
                raise NotFoundError("Product not found for order item.")

            await self.inventory_service.reserve_stock(product_id=product.id, quantity=quantity)

            line_total = product.price_amount * quantity
            subtotal += line_total
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    quantity=quantity,
                    unit_price_amount=product.price_amount,
                    line_total_amount=line_total,
                )
            )

        total = subtotal + tax_amount + shipping_amount - discount_amount
        if total < 0:
            raise BusinessRuleError("Order total cannot be negative.")

        return await self.order_repository.create(
            {
                "order_number": self._generate_order_number(),
                "customer_id": customer_id,
                "status": OrderStatus.PENDING,
                "fulfillment_status": FulfillmentStatus.READY_TO_PICK,
                "payment_status": PaymentStatus.UNPAID,
                "subtotal_amount": subtotal,
                "tax_amount": tax_amount,
                "shipping_amount": shipping_amount,
                "discount_amount": discount_amount,
                "total_amount": total,
                "currency": currency,
                "shipping_name": shipping_name,
                "shipping_address": shipping_address,
                "placed_at": datetime.now(UTC),
                "items": order_items,
            }
        )

    async def update_status(self, *, order_id: UUID, status: OrderStatus | str) -> Order:
        order = await self.get_order(order_id)
        current_status = OrderStatus(order.status)
        next_status = OrderStatus(status)
        if next_status not in self.ALLOWED_STATUS_TRANSITIONS[current_status]:
            raise BusinessRuleError("Invalid order status transition.")

        update_data: dict[str, object] = {"status": next_status}
        if next_status == OrderStatus.FULFILLED:
            update_data["fulfilled_at"] = datetime.now(UTC)
        if next_status == OrderStatus.CANCELLED:
            update_data["cancelled_at"] = datetime.now(UTC)
            for item in order.items:
                await self.inventory_service.release_reserved_stock(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
        return await self.order_repository.update(order, update_data)

    def calculate_totals(
        self,
        *,
        line_totals: Sequence[Decimal],
        tax_amount: Decimal = Decimal("0.00"),
        shipping_amount: Decimal = Decimal("0.00"),
        discount_amount: Decimal = Decimal("0.00"),
    ) -> dict[str, Decimal]:
        subtotal = sum(line_totals, Decimal("0.00"))
        total = subtotal + tax_amount + shipping_amount - discount_amount
        if total < 0:
            raise BusinessRuleError("Order total cannot be negative.")
        return {
            "subtotal_amount": subtotal,
            "tax_amount": tax_amount,
            "shipping_amount": shipping_amount,
            "discount_amount": discount_amount,
            "total_amount": total,
        }

    def _generate_order_number(self) -> str:
        return f"ORD-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:8].upper()}"
