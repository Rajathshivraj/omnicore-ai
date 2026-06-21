from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession
from app.modules.auth.dependencies import require_permissions
from app.modules.inventory.repository import InventoryMovementRepository, InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreateRequest,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdateRequest,
)
from app.modules.orders.service import OrderService
from app.modules.products.repository import ProductRepository
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_order_service(session: DbSession) -> OrderService:
    inventory_service = InventoryService(
        inventory_repository=InventoryRepository(session),
        movement_repository=InventoryMovementRepository(session),
    )
    return OrderService(
        order_repository=OrderRepository(session),
        product_repository=ProductRepository(session),
        inventory_service=inventory_service,
    )


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List all orders",
    description="Returns paginated operational order records. Requires permission to view all orders.",
)
async def list_orders(
    service: OrderServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_ALL_ORDERS))],
    customer_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    fulfillment_status: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> OrderListResponse:
    items = await service.list_orders(
        customer_id=customer_id,
        status=status,
        fulfillment_status=fulfillment_status,
        search=search,
        offset=offset,
        limit=limit,
    )
    return OrderListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
    summary="Create order",
    description="Creates a customer order and reserves stock through the order service.",
)
async def create_order(
    payload: OrderCreateRequest,
    service: OrderServiceDep,
    session: DbSession,
    current_user: Annotated[User, Depends(require_permissions(Permission.CREATE_ORDERS))],
) -> object:
    order = await service.create_order(
        customer_id=current_user.id,
        items=[item.model_dump() for item in payload.items],
        tax_amount=payload.tax_amount,
        shipping_amount=payload.shipping_amount,
        discount_amount=payload.discount_amount,
        currency=payload.currency,
        shipping_name=payload.shipping_name,
        shipping_address=payload.shipping_address,
    )
    await session.commit()
    return await service.get_order(order.id)


@router.get(
    "/me",
    response_model=OrderListResponse,
    summary="List my orders",
    description="Returns orders owned by the authenticated customer.",
)
async def list_my_orders(
    service: OrderServiceDep,
    current_user: Annotated[User, Depends(require_permissions(Permission.VIEW_OWN_ORDERS))],
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> OrderListResponse:
    items = await service.list_orders(
        customer_id=current_user.id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return OrderListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.get("/me/{order_id}", response_model=OrderResponse, summary="Get my order")
async def get_my_order(
    order_id: UUID,
    service: OrderServiceDep,
    current_user: Annotated[User, Depends(require_permissions(Permission.VIEW_OWN_ORDERS))],
) -> object:
    return await service.get_customer_order(order_id=order_id, customer_id=current_user.id)


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order")
async def get_order(
    order_id: UUID,
    service: OrderServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_ALL_ORDERS))],
) -> object:
    return await service.get_order(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse, summary="Update order status")
async def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateRequest,
    service: OrderServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_FULFILLMENT))],
) -> object:
    order = await service.update_status(order_id=order_id, status=payload.status)
    await session.commit()
    return await service.get_order(order.id)
