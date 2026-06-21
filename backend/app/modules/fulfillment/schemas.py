from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import FulfillmentStatus
from app.schemas.pagination import PaginatedResponse


class FulfillmentCreateRequest(BaseModel):
    order_id: UUID
    warehouse_code: str = Field(default="default", min_length=1, max_length=80)


class FulfillmentUpdateRequest(BaseModel):
    status: FulfillmentStatus
    tracking_reference: str | None = Field(default=None, max_length=120)
    exception_reason: str | None = None


class FulfillmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    status: str
    warehouse_code: str
    tracking_reference: str | None
    exception_reason: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


FulfillmentListResponse = PaginatedResponse[FulfillmentResponse]
