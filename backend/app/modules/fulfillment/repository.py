from collections.abc import Sequence
from uuid import UUID

from app.modules.fulfillment.models import FulfillmentRecord
from app.repositories.base import BaseRepository


class FulfillmentRepository(BaseRepository[FulfillmentRecord]):
    """Persistence boundary for fulfillment queue records."""

    model_class = FulfillmentRecord

    async def list_filtered(
        self,
        *,
        status: str | None = None,
        warehouse_code: str | None = None,
        order_id: UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[FulfillmentRecord]:
        statement = self.base_statement()
        if status:
            statement = statement.where(FulfillmentRecord.status == status)
        if warehouse_code:
            statement = statement.where(FulfillmentRecord.warehouse_code == warehouse_code)
        if order_id:
            statement = statement.where(FulfillmentRecord.order_id == order_id)
        result = await self.session.execute(
            statement.order_by(FulfillmentRecord.created_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()
