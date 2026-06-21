from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import FulfillmentStatus, OrderStatus, PaymentStatus
from app.schemas.pagination import PaginatedResponse


class OrderItemCreateRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    items: list[OrderItemCreateRequest] = Field(min_length=1)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    shipping_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    shipping_name: str | None = Field(default=None, max_length=160)
    shipping_address: dict[str, object] | None = None


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    sku_snapshot: str
    product_name_snapshot: str
    quantity: int
    unit_price_amount: Decimal
    line_total_amount: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    customer_id: UUID
    status: str
    fulfillment_status: str
    payment_status: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    shipping_name: str | None
    shipping_address: dict[str, object] | None
    placed_at: datetime
    fulfilled_at: datetime | None
    cancelled_at: datetime | None
    items: list[OrderItemResponse] = Field(default_factory=list)


OrderListResponse = PaginatedResponse[OrderResponse]
