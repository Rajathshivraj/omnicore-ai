from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import InventoryStatus, enum_type
from app.db.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.products.models import Product


class Inventory(UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("stock_on_hand >= 0", name="stock_on_hand_non_negative"),
        CheckConstraint("stock_reserved >= 0", name="stock_reserved_non_negative"),
        CheckConstraint("stock_available >= 0", name="stock_available_non_negative"),
        CheckConstraint("reorder_point >= 0", name="reorder_point_non_negative"),
        CheckConstraint(
            "reorder_quantity IS NULL OR reorder_quantity >= 0",
            name="reorder_quantity_non_negative",
        ),
        CheckConstraint("stock_reserved <= stock_on_hand", name="reserved_not_above_on_hand"),
        UniqueConstraint("product_id", "location_code", name="uq_inventory_product_location"),
        Index("ix_inventory_status_available", "inventory_status", "stock_available"),
    )

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    location_code: Mapped[str] = mapped_column(String(80), nullable=False, default="default")
    stock_on_hand: Mapped[int] = mapped_column(nullable=False, default=0)
    stock_reserved: Mapped[int] = mapped_column(nullable=False, default=0)
    stock_available: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_quantity: Mapped[int | None] = mapped_column(nullable=True)
    inventory_status: Mapped[InventoryStatus] = mapped_column(
        enum_type(InventoryStatus, name="inventory_status"),
        nullable=False,
        default=InventoryStatus.HEALTHY,
        index=True,
    )
    last_counted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="inventory_records")
    movements: Mapped[list["InventoryMovement"]] = relationship("InventoryMovement", back_populates="inventory")


class InventoryMovement(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        CheckConstraint("quantity_delta != 0", name="inventory_movement_delta_non_zero"),
        Index("ix_inventory_movements_inventory_created", "inventory_id", "created_at"),
        Index("ix_inventory_movements_product_created", "product_id", "created_at"),
    )

    inventory_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    movement_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity_delta: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="movements")
