from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession
from app.modules.auth.dependencies import require_permissions
from app.modules.fulfillment.repository import FulfillmentRepository
from app.modules.fulfillment.schemas import (
    FulfillmentCreateRequest,
    FulfillmentListResponse,
    FulfillmentResponse,
    FulfillmentUpdateRequest,
)
from app.modules.fulfillment.service import FulfillmentService
from app.modules.orders.repository import OrderRepository
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/fulfillment", tags=["fulfillment"])


async def get_fulfillment_service(session: DbSession) -> FulfillmentService:
    return FulfillmentService(
        fulfillment_repository=FulfillmentRepository(session),
        order_repository=OrderRepository(session),
    )


FulfillmentServiceDep = Annotated[FulfillmentService, Depends(get_fulfillment_service)]


@router.get("", response_model=FulfillmentListResponse, summary="List fulfillment queue")
async def list_fulfillment_records(
    service: FulfillmentServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_FULFILLMENT))],
    status: str | None = Query(default=None),
    warehouse_code: str | None = Query(default=None, min_length=1, max_length=80),
    order_id: UUID | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> FulfillmentListResponse:
    items = await service.list_records(
        status=status,
        warehouse_code=warehouse_code,
        order_id=order_id,
        offset=offset,
        limit=limit,
    )
    return FulfillmentListResponse(
        items=list(items),
        meta=PageMeta(offset=offset, limit=limit, count=len(items)),
    )


@router.post("", response_model=FulfillmentResponse, status_code=201, summary="Create fulfillment")
async def create_fulfillment_record(
    payload: FulfillmentCreateRequest,
    service: FulfillmentServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_FULFILLMENT))],
) -> object:
    record = await service.create_record(payload.model_dump())
    await session.commit()
    return record


@router.patch("/{record_id}", response_model=FulfillmentResponse, summary="Update fulfillment")
async def update_fulfillment_record(
    record_id: UUID,
    payload: FulfillmentUpdateRequest,
    service: FulfillmentServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.MANAGE_FULFILLMENT))],
) -> object:
    record = await service.update_record(record_id=record_id, **payload.model_dump())
    await session.commit()
    return record
