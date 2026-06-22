from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import ProductStatus, enum_type
from app.db.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.copilot.models import AIInsight
    from app.modules.forecasting.models import Forecast
    from app.modules.inventory.models import Inventory
    from app.modules.orders.models import OrderItem


class Category(UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        Index(
            "uq_categories_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    parent_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[ProductStatus] = mapped_column(
        enum_type(ProductStatus, name="category_status"),
        nullable=False,
        default=ProductStatus.ACTIVE,
    )

    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_amount >= 0", name="price_amount_non_negative"),
        CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="cost_amount_non_negative"),
        Index("uq_products_sku_active", "sku", unique=True, postgresql_where=text("deleted_at IS NULL")),
        Index("uq_products_slug_active", "slug", unique=True, postgresql_where=text("deleted_at IS NULL")),
    )

    category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        enum_type(ProductStatus, name="product_status"),
        nullable=False,
        default=ProductStatus.ACTIVE,
        index=True,
    )
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    inventory_records: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")
    forecasts: Mapped[list["Forecast"]] = relationship("Forecast", back_populates="product")
    ai_insights: Mapped[list["AIInsight"]] = relationship("AIInsight", back_populates="product")
