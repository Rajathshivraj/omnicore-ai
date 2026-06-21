from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.enums import AIInsightType, ReviewStatus
from app.schemas.pagination import PaginatedResponse


class AIInsightCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1)
    suggested_action: str | None = None
    confidence_score: Decimal | None = Field(default=None, ge=0, le=100)
    product_id: UUID | None = None
    order_id: UUID | None = None
    forecast_id: UUID | None = None
    source_refs: list[dict[str, Any]] | None = None
    input_snapshot: dict[str, Any] | None = None
    model_name: str | None = Field(default=None, max_length=120)
    model_version: str | None = Field(default=None, max_length=80)
    generated_at: datetime | None = None


class CopilotAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class KnowledgeDocumentRequest(BaseModel):
    source_id: str = Field(min_length=1, max_length=160)
    source_type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


class KnowledgeIndexRequest(BaseModel):
    documents: list[KnowledgeDocumentRequest] = Field(min_length=1, max_length=50)


class KnowledgeIndexResponse(BaseModel):
    indexed_chunks: int


class AIInsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    insight_type: str
    status: str
    title: str
    summary: str
    suggested_action: str | None
    confidence_score: Decimal | None
    product_id: UUID | None
    order_id: UUID | None
    forecast_id: UUID | None
    source_refs: list[dict[str, Any]]
    input_snapshot: dict[str, Any]
    model_name: str | None
    model_version: str | None
    generated_at: datetime
    reviewed_at: datetime | None
    reviewed_by_id: UUID | None


AIInsightListResponse = PaginatedResponse[AIInsightResponse]
