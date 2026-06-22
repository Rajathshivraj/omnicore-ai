from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import ForecastStatus, enum_type
from app.db.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.copilot.models import AIInsight
    from app.modules.products.models import Product
    from app.modules.users.models import User


class Forecast(UUIDPrimaryKeyMixin, SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        CheckConstraint("predicted_demand >= 0", name="predicted_demand_non_negative"),
        CheckConstraint(
            "suggested_reorder_quantity >= 0",
            name="suggested_reorder_quantity_non_negative",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)",
            name="confidence_score_percent",
        ),
        CheckConstraint(
            "forecast_period_end >= forecast_period_start",
            name="forecast_period_valid",
        ),
        Index("ix_forecasts_product_generated_at", "product_id", "generated_at"),
        Index("ix_forecasts_period", "forecast_period_start", "forecast_period_end"),
        Index("ix_forecasts_status_generated_at", "status", "generated_at"),
    )

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    forecast_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    forecast_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_demand: Mapped[int] = mapped_column(nullable=False)
    suggested_reorder_quantity: Mapped[int] = mapped_column(nullable=False)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    source_window_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_window_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ForecastStatus] = mapped_column(
        enum_type(ForecastStatus, name="forecast_status"),
        nullable=False,
        default=ForecastStatus.PENDING,
        index=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    product: Mapped["Product"] = relationship(back_populates="forecasts")
    reviewer: Mapped["User | None"] = relationship(
        back_populates="reviewed_forecasts",
        foreign_keys=[reviewed_by_id],
    )
    ai_insights: Mapped[list["AIInsight"]] = relationship(back_populates="forecast")
