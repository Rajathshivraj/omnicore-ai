from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.modules.forecasting.models import Forecast
from app.modules.products.models import Product


class ForecastRepository(BaseRepository[Forecast]):
    """Persistence boundary for forecast output records."""

    model_class = Forecast

    async def get_latest_for_product(
        self,
        product_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Forecast | None:
        statement = (
            self.base_statement(include_deleted=include_deleted)
            .where(Forecast.product_id == product_id)
            .order_by(Forecast.generated_at.desc())
            .limit(1)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        *,
        product_id: UUID | None = None,
        status: str | None = None,
        period_start: date | None = None,
        period_end: date | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> Sequence[Forecast]:
        statement = self.base_statement(include_deleted=include_deleted)
        if search:
            statement = statement.join(Product)
        if product_id:
            statement = statement.where(Forecast.product_id == product_id)
        if status:
            statement = statement.where(Forecast.status == status)
        if period_start:
            statement = statement.where(Forecast.forecast_period_start >= period_start)
        if period_end:
            statement = statement.where(Forecast.forecast_period_end <= period_end)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
            )
        result = await self.session.execute(
            statement.order_by(Forecast.generated_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()
