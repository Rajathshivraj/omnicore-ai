from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.enums import UserStatus, enum_type
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.copilot.models import AIInsight
    from app.modules.forecasting.models import Forecast
    from app.modules.orders.models import Order


class Role(UUIDPrimaryKeyMixin, SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        Index("uq_roles_name_active", "name", unique=True, postgresql_where=text("deleted_at IS NULL")),
        Index("uq_roles_slug_active", "slug", unique=True, postgresql_where=text("deleted_at IS NULL")),
    )

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    permissions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    users: Mapped[list[User]] = relationship(
        back_populates="role",
        foreign_keys="User.role_id",
    )


class User(UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("uq_users_email_active", "email", unique=True, postgresql_where=text("deleted_at IS NULL")),
    )

    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        enum_type(UserStatus, name="user_status"),
        nullable=False,
        default=UserStatus.INVITED,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    role: Mapped[Role] = relationship(back_populates="users", foreign_keys=[role_id])
    orders: Mapped[list[Order]] = relationship(
        back_populates="customer",
        foreign_keys="Order.customer_id",
    )
    reviewed_forecasts: Mapped[list[Forecast]] = relationship(
        back_populates="reviewer",
        foreign_keys="Forecast.reviewed_by_id",
    )
    reviewed_ai_insights: Mapped[list[AIInsight]] = relationship(
        back_populates="reviewer",
        foreign_keys="AIInsight.reviewed_by_id",
    )
