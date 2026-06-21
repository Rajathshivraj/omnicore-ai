"""initial schema

Revision ID: 202606220001
Revises:
Create Date: 2026-06-22
"""

# ruff: noqa: E501

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202606220001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def audit_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    ]


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissions", postgresql.JSONB(), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_roles_slug", "roles", ["slug"])
    op.create_index(
        "uq_roles_name_active",
        "roles",
        ["name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "uq_roles_slug_active",
        "roles",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profile_metadata", postgresql.JSONB(), nullable=False),
        *audit_columns(),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_foreign_key("fk_roles_deleted_by_id_users", "roles", "users", ["deleted_by_id"], ["id"])
    for table in ("users",):
        op.create_foreign_key(f"fk_{table}_created_by_id_users", table, "users", ["created_by_id"], ["id"])
        op.create_foreign_key(f"fk_{table}_updated_by_id_users", table, "users", ["updated_by_id"], ["id"])
        op.create_foreign_key(f"fk_{table}_deleted_by_id_users", table, "users", ["deleted_by_id"], ["id"])

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *audit_columns(),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_index(
        "uq_categories_slug_active",
        "categories",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("attributes", postgresql.JSONB(), nullable=False),
        *audit_columns(),
        sa.CheckConstraint("price_amount >= 0", name="price_amount_non_negative"),
        sa.CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="cost_amount_non_negative"),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index(
        "uq_products_sku_active",
        "products",
        ["sku"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "uq_products_slug_active",
        "products",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "inventory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("location_code", sa.String(length=80), nullable=False),
        sa.Column("stock_on_hand", sa.Integer(), nullable=False),
        sa.Column("stock_reserved", sa.Integer(), nullable=False),
        sa.Column("stock_available", sa.Integer(), nullable=False),
        sa.Column("reorder_point", sa.Integer(), nullable=False),
        sa.Column("reorder_quantity", sa.Integer(), nullable=True),
        sa.Column("inventory_status", sa.String(length=32), nullable=False),
        sa.Column("last_counted_at", sa.DateTime(timezone=True), nullable=True),
        *audit_columns(),
        sa.CheckConstraint("stock_on_hand >= 0", name="stock_on_hand_non_negative"),
        sa.CheckConstraint("stock_reserved >= 0", name="stock_reserved_non_negative"),
        sa.CheckConstraint("stock_available >= 0", name="stock_available_non_negative"),
        sa.CheckConstraint("stock_reserved <= stock_on_hand", name="reserved_not_above_on_hand"),
        sa.CheckConstraint("reorder_point >= 0", name="reorder_point_non_negative"),
        sa.UniqueConstraint("product_id", "location_code", name="uq_inventory_product_location"),
    )
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"])
    op.create_index("ix_inventory_status_available", "inventory", ["inventory_status", "stock_available"])

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_number", sa.String(length=40), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("fulfillment_status", sa.String(length=32), nullable=False),
        sa.Column("payment_status", sa.String(length=32), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("shipping_name", sa.String(length=160), nullable=True),
        sa.Column("shipping_address", postgresql.JSONB(), nullable=True),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        *audit_columns(),
        sa.UniqueConstraint("order_number", name="uq_orders_order_number"),
        sa.CheckConstraint("subtotal_amount >= 0", name="subtotal_amount_non_negative"),
        sa.CheckConstraint("tax_amount >= 0", name="tax_amount_non_negative"),
        sa.CheckConstraint("shipping_amount >= 0", name="shipping_amount_non_negative"),
        sa.CheckConstraint("discount_amount >= 0", name="discount_amount_non_negative"),
        sa.CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
    )
    op.create_index("ix_orders_customer_placed_at", "orders", ["customer_id", "placed_at"])
    op.create_index("ix_orders_status_placed_at", "orders", ["status", "placed_at"])
    op.create_index(
        "ix_orders_fulfillment_status_placed_at",
        "orders",
        ["fulfillment_status", "placed_at"],
    )

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("sku_snapshot", sa.String(length=80), nullable=False),
        sa.Column("product_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total_amount", sa.Numeric(12, 2), nullable=False),
        *timestamp_columns(),
        sa.CheckConstraint("quantity > 0", name="quantity_positive"),
        sa.CheckConstraint("unit_price_amount >= 0", name="unit_price_amount_non_negative"),
        sa.CheckConstraint("line_total_amount >= 0", name="line_total_amount_non_negative"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])

    op.create_table(
        "inventory_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inventory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("movement_type", sa.String(length=40), nullable=False),
        sa.Column("quantity_delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        *audit_columns()[:4],
        sa.CheckConstraint("quantity_delta != 0", name="inventory_movement_delta_non_zero"),
    )
    op.create_index("ix_inventory_movements_inventory_created", "inventory_movements", ["inventory_id", "created_at"])
    op.create_index("ix_inventory_movements_product_created", "inventory_movements", ["product_id", "created_at"])

    op.create_table(
        "fulfillment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("warehouse_code", sa.String(length=80), nullable=False),
        sa.Column("tracking_reference", sa.String(length=120), nullable=True),
        sa.Column("exception_reason", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *audit_columns()[:4],
    )
    op.create_index("ix_fulfillment_records_order_id", "fulfillment_records", ["order_id"])
    op.create_index("ix_fulfillment_records_status_created", "fulfillment_records", ["status", "created_at"])

    op.create_table(
        "forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("forecast_period_start", sa.Date(), nullable=False),
        sa.Column("forecast_period_end", sa.Date(), nullable=False),
        sa.Column("predicted_demand", sa.Integer(), nullable=False),
        sa.Column("suggested_reorder_quantity", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("source_window_start", sa.Date(), nullable=True),
        sa.Column("source_window_end", sa.Date(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *timestamp_columns(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("predicted_demand >= 0", name="predicted_demand_non_negative"),
        sa.CheckConstraint(
            "suggested_reorder_quantity >= 0",
            name="suggested_reorder_quantity_non_negative",
        ),
        sa.CheckConstraint("forecast_period_end >= forecast_period_start", name="forecast_period_valid"),
    )
    op.create_index("ix_forecasts_product_generated_at", "forecasts", ["product_id", "generated_at"])
    op.create_index("ix_forecasts_period", "forecasts", ["forecast_period_start", "forecast_period_end"])
    op.create_index("ix_forecasts_status_generated_at", "forecasts", ["status", "generated_at"])

    op.create_table(
        "ai_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("insight_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("forecast_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("forecasts.id"), nullable=True),
        sa.Column("source_refs", postgresql.JSONB(), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("model_version", sa.String(length=80), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *timestamp_columns(),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_ai_insights_status_generated_at", "ai_insights", ["status", "generated_at"])
    op.create_index("ix_ai_insights_type_generated_at", "ai_insights", ["insight_type", "generated_at"])

    for table in ("categories", "products", "inventory", "orders"):
        op.create_foreign_key(f"fk_{table}_created_by_id_users", table, "users", ["created_by_id"], ["id"])
        op.create_foreign_key(f"fk_{table}_updated_by_id_users", table, "users", ["updated_by_id"], ["id"])
        op.create_foreign_key(f"fk_{table}_deleted_by_id_users", table, "users", ["deleted_by_id"], ["id"])


def downgrade() -> None:
    for table in (
        "ai_insights",
        "forecasts",
        "fulfillment_records",
        "inventory_movements",
        "order_items",
        "orders",
        "inventory",
        "products",
        "categories",
        "users",
        "roles",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
