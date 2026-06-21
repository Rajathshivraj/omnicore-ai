from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import AIInsightType, ReviewStatus, enum_type
from app.db.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from uuid import UUID

    from app.modules.forecasting.models import Forecast
    from app.modules.orders.models import Order
    from app.modules.products.models import Product
    from app.modules.users.models import User


class AIInsight(UUIDPrimaryKeyMixin, SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "ai_insights"
    __table_args__ = (
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)",
            name="confidence_score_percent",
        ),
        Index("ix_ai_insights_status_generated_at", "status", "generated_at"),
        Index("ix_ai_insights_type_generated_at", "insight_type", "generated_at"),
    )

    insight_type: Mapped[AIInsightType] = mapped_column(
        enum_type(AIInsightType, name="ai_insight_type", length=40),
        nullable=False,
        index=True,
    )
    status: Mapped[ReviewStatus] = mapped_column(
        enum_type(ReviewStatus, name="ai_insight_review_status"),
        nullable=False,
        default=ReviewStatus.NEW,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    forecast_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("forecasts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    product: Mapped[Product | None] = relationship(back_populates="ai_insights")
    order: Mapped[Order | None] = relationship(back_populates="ai_insights")
    forecast: Mapped[Forecast | None] = relationship(back_populates="ai_insights")
    reviewer: Mapped[User | None] = relationship(
        back_populates="reviewed_ai_insights",
        foreign_keys=[reviewed_by_id],
    )
