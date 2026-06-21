from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession
from app.modules.auth.dependencies import require_permissions
from app.modules.inventory.repository import InventoryMovementRepository, InventoryRepository
from app.modules.inventory.schemas import (
    InventoryCreateRequest,
    InventoryListResponse,
    InventoryResponse,
    InventoryUpdateRequest,
    StockAdjustmentRequest,
)
from app.modules.inventory.service import InventoryService
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/inventory", tags=["inventory"])


async def get_inventory_service(session: DbSession) -> InventoryService:
    return InventoryService(
        inventory_repository=InventoryRepository(session),
        movement_repository=InventoryMovementRepository(session),
    )


InventoryServiceDep = Annotated[InventoryService, Depends(get_inventory_service)]


@router.get(
    "",
    response_model=InventoryListResponse,
    summary="List inventory",
    description="Returns paginated inventory records with status, location, low-stock, and product search filters.",
)
async def list_inventory(
    service: InventoryServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_INVENTORY))],
    status: str | None = Query(default=None),
    location_code: str | None = Query(default=None, min_length=1, max_length=80),
    low_stock_only: bool = Query(default=False),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> InventoryListResponse:
    items = await service.list_inventory(
        status=status,
        location_code=location_code,
        low_stock_only=low_stock_only,
        search=search,
        offset=offset,
        limit=limit,
    )
    return InventoryListResponse(items=list(items), meta=PageMeta(offset=offset, limit=limit, count=len(items)))


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=201,
    summary="Create inventory record",
    description="Creates a stock position for a product and location.",
)
async def create_inventory(
    payload: InventoryCreateRequest,
    service: InventoryServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_INVENTORY))],
) -> object:
    inventory = await service.create_inventory(payload.model_dump())
    await session.commit()
    return inventory


@router.get("/{inventory_id}", response_model=InventoryResponse, summary="Get inventory record")
async def get_inventory(
    inventory_id: UUID,
    service: InventoryServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_INVENTORY))],
) -> object:
    return await service.get_inventory(inventory_id)


@router.patch("/{inventory_id}", response_model=InventoryResponse, summary="Update inventory metadata")
async def update_inventory(
    inventory_id: UUID,
    payload: InventoryUpdateRequest,
    service: InventoryServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_INVENTORY))],
) -> object:
    inventory = await service.update_inventory(
        inventory_id,
        payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    return inventory


@router.post("/{inventory_id}/adjustments", response_model=InventoryResponse, summary="Adjust stock")
async def adjust_stock(
    inventory_id: UUID,
    payload: StockAdjustmentRequest,
    service: InventoryServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_INVENTORY))],
) -> object:
    inventory = await service.adjust_stock(
        inventory_id=inventory_id,
        quantity_delta=payload.quantity_delta,
        reason="Manual stock adjustment",
    )
    await session.commit()
    return inventory
