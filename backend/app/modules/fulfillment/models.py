from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import FulfillmentStatus, enum_type
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.orders.models import Order


class FulfillmentRecord(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "fulfillment_records"
    __table_args__ = (
        Index("ix_fulfillment_records_status_created", "status", "created_at"),
        Index("ix_fulfillment_records_order_id", "order_id"),
    )

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[FulfillmentStatus] = mapped_column(
        enum_type(FulfillmentStatus, name="fulfillment_record_status"),
        nullable=False,
        default=FulfillmentStatus.READY_TO_PICK,
        index=True,
    )
    warehouse_code: Mapped[str] = mapped_column(String(80), nullable=False, default="default")
    tracking_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    exception_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="fulfillment_records")
