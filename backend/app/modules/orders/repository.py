from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.modules.orders.models import Order
from app.modules.users.models import User


class OrderRepository(BaseRepository[Order]):
    """Persistence boundary for orders and order items."""

    model_class = Order

    async def get_by_id_with_items(
        self,
        order_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Order | None:
        statement = (
            self.base_statement(include_deleted=include_deleted)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_order_number(
        self,
        order_number: str,
        *,
        include_deleted: bool = False,
    ) -> Order | None:
        statement = self.base_statement(include_deleted=include_deleted).where(
            Order.order_number == order_number
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        customer_id: UUID | None = None,
        status: str | None = None,
        fulfillment_status: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Order]:
        statement = self.base_statement(include_deleted=include_deleted).options(
            selectinload(Order.items)
        )
        if search:
            statement = statement.join(User, Order.customer_id == User.id)
        if customer_id:
            statement = statement.where(Order.customer_id == customer_id)
        if status:
            statement = statement.where(Order.status == status)
        if fulfillment_status:
            statement = statement.where(Order.fulfillment_status == fulfillment_status)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Order.order_number.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
        result = await self.session.execute(
            statement.order_by(Order.placed_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()
