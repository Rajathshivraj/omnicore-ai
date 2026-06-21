from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import ForecastStatus
from app.schemas.pagination import PaginatedResponse


class ForecastCreateRequest(BaseModel):
    product_id: UUID
    forecast_period_start: date
    forecast_period_end: date
    predicted_demand: int = Field(ge=0)
    suggested_reorder_quantity: int = Field(ge=0)
    model_name: str = Field(min_length=1, max_length=120)
    model_version: str = Field(min_length=1, max_length=80)
    confidence_score: Decimal | None = Field(default=None, ge=0, le=100)
    source_window_start: date | None = None
    source_window_end: date | None = None
    generated_at: datetime | None = None


class ForecastGenerateRequest(BaseModel):
    product_ids: list[UUID] | None = Field(default=None, max_length=100)
    forecast_period_start: date | None = None
    forecast_days: int = Field(default=30, ge=1, le=120)
    source_window_days: int = Field(default=90, ge=14, le=365)
    location_code: str = Field(default="default", min_length=1, max_length=80)


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    forecast_period_start: date
    forecast_period_end: date
    predicted_demand: int
    suggested_reorder_quantity: int
    confidence_score: Decimal | None
    model_name: str
    model_version: str
    source_window_start: date | None
    source_window_end: date | None
    generated_at: datetime
    status: str
    failure_reason: str | None
    reviewed_at: datetime | None
    reviewed_by_id: UUID | None


ForecastListResponse = PaginatedResponse[ForecastResponse]
