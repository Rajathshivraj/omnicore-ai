from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.enums import InventoryStatus
from app.schemas.pagination import PaginatedResponse


class InventoryCreateRequest(BaseModel):
    product_id: UUID
    location_code: str = Field(default="default", min_length=1, max_length=80)
    stock_on_hand: int = Field(default=0, ge=0)
    stock_reserved: int = Field(default=0, ge=0)
    stock_available: int | None = Field(default=None, ge=0)
    reorder_point: int = Field(default=0, ge=0)
    reorder_quantity: int | None = Field(default=None, ge=0)
    inventory_status: InventoryStatus = InventoryStatus.HEALTHY


class InventoryUpdateRequest(BaseModel):
    location_code: str | None = Field(default=None, min_length=1, max_length=80)
    reorder_point: int | None = Field(default=None, ge=0)
    reorder_quantity: int | None = Field(default=None, ge=0)
    inventory_status: InventoryStatus | None = None


class StockAdjustmentRequest(BaseModel):
    quantity_delta: int

    @field_validator("quantity_delta")
    @classmethod
    def quantity_delta_must_not_be_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("quantity_delta must not be zero")
        return value


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    location_code: str
    stock_on_hand: int
    stock_reserved: int
    stock_available: int
    reorder_point: int
    reorder_quantity: int | None
    inventory_status: str


InventoryListResponse = PaginatedResponse[InventoryResponse]
