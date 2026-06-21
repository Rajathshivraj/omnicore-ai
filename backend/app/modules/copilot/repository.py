from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.modules.copilot.models import AIInsight


class AIInsightRepository(BaseRepository[AIInsight]):
    """Persistence boundary for AI insight and recommendation records."""

    model_class = AIInsight

    async def list_filtered(
        self,
        *,
        insight_type: str | None = None,
        status: str | None = None,
        product_id: UUID | None = None,
        order_id: UUID | None = None,
        forecast_id: UUID | None = None,
        reviewed_by_id: UUID | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[AIInsight]:
        statement = self.base_statement(include_deleted=include_deleted)
        if insight_type:
            statement = statement.where(AIInsight.insight_type == insight_type)
        if status:
            statement = statement.where(AIInsight.status == status)
        if product_id:
            statement = statement.where(AIInsight.product_id == product_id)
        if order_id:
            statement = statement.where(AIInsight.order_id == order_id)
        if forecast_id:
            statement = statement.where(AIInsight.forecast_id == forecast_id)
        if reviewed_by_id:
            statement = statement.where(AIInsight.reviewed_by_id == reviewed_by_id)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(AIInsight.title.ilike(pattern), AIInsight.summary.ilike(pattern))
            )
        result = await self.session.execute(
            statement.order_by(AIInsight.generated_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()
