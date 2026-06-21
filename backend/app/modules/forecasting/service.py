from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from app.core.errors import BusinessRuleError, NotFoundError
from app.db.enums import ForecastStatus
from app.integrations.ai.forecasting_service import (
    ForecastingInput,
    ForecastingIntegrationService,
    HistoricalDemandPoint,
)
from app.modules.forecasting.models import Forecast
from app.modules.forecasting.repository import ForecastRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository


class ForecastService:
    """Coordinates forecast outputs, review workflow, and replenishment signals."""

    def __init__(
        self,
        forecast_repository: ForecastRepository,
        product_repository: ProductRepository,
        order_repository: OrderRepository | None = None,
        inventory_repository: InventoryRepository | None = None,
        forecasting_provider: ForecastingIntegrationService | None = None,
    ) -> None:
        self.forecast_repository = forecast_repository
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.inventory_repository = inventory_repository
        self.forecasting_provider = forecasting_provider or ForecastingIntegrationService()

    async def store_forecast_output(
        self,
        *,
        product_id: UUID,
        forecast_period_start: date,
        forecast_period_end: date,
        predicted_demand: int,
        suggested_reorder_quantity: int,
        model_name: str,
        model_version: str,
        confidence_score: Decimal | None = None,
        source_window_start: date | None = None,
        source_window_end: date | None = None,
        generated_at: datetime | None = None,
    ) -> Forecast:
        if forecast_period_end < forecast_period_start:
            raise BusinessRuleError("Forecast period end cannot be before start.")
        if predicted_demand < 0:
            raise BusinessRuleError("Predicted demand cannot be negative.")
        if suggested_reorder_quantity < 0:
            raise BusinessRuleError("Suggested reorder quantity cannot be negative.")
        if confidence_score is not None and not Decimal("0") <= confidence_score <= Decimal("100"):
            raise BusinessRuleError("Forecast confidence score must be between 0 and 100.")

        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise NotFoundError("Product not found for forecast.")

        return await self.forecast_repository.create(
            {
                "product_id": product_id,
                "forecast_period_start": forecast_period_start,
                "forecast_period_end": forecast_period_end,
                "predicted_demand": predicted_demand,
                "suggested_reorder_quantity": suggested_reorder_quantity,
                "confidence_score": confidence_score,
                "model_name": model_name,
                "model_version": model_version,
                "source_window_start": source_window_start,
                "source_window_end": source_window_end,
                "generated_at": generated_at or datetime.now(UTC),
                "status": ForecastStatus.COMPLETED,
            }
        )

    async def generate_forecasts(
        self,
        *,
        product_ids: list[UUID] | None = None,
        forecast_period_start: date | None = None,
        forecast_days: int = 30,
        source_window_days: int = 90,
        location_code: str = "default",
    ) -> Sequence[Forecast]:
        if self.order_repository is None or self.inventory_repository is None:
            raise BusinessRuleError("Forecast generation service is not fully configured.")
        if forecast_days < 1:
            raise BusinessRuleError("Forecast horizon must be at least one day.")

        period_start = forecast_period_start or date.today()
        period_end = period_start + timedelta(days=forecast_days - 1)
        source_window_start = period_start - timedelta(days=source_window_days)
        source_window_end = period_start - timedelta(days=1)

        products = []
        if product_ids:
            for product_id in product_ids:
                product = await self.product_repository.get_by_id(product_id)
                if product is None:
                    raise NotFoundError("Product not found for forecast generation.")
                products.append(product)
        else:
            products = list(await self.product_repository.list_filtered(status="active", limit=100))

        orders = await self.order_repository.list_filtered(offset=0, limit=500)
        forecasts: list[Forecast] = []
        for product in products:
            inventory = await self.inventory_repository.get_by_product_location(
                product_id=product.id,
                location_code=location_code,
            )
            history = [
                HistoricalDemandPoint(demand_date=order.placed_at.date(), quantity=item.quantity)
                for order in orders
                if source_window_start <= order.placed_at.date() <= source_window_end
                for item in order.items
                if item.product_id == product.id
            ]
            result = await self.forecasting_provider.generate(
                ForecastingInput(
                    product_id=str(product.id),
                    current_available=inventory.stock_available if inventory else 0,
                    reorder_point=inventory.reorder_point if inventory else 0,
                    reorder_quantity=inventory.reorder_quantity if inventory else None,
                    forecast_period_start=period_start,
                    forecast_period_end=period_end,
                    history=history,
                )
            )
            forecasts.append(
                await self.store_forecast_output(
                    product_id=product.id,
                    forecast_period_start=period_start,
                    forecast_period_end=period_end,
                    predicted_demand=result.predicted_demand,
                    suggested_reorder_quantity=result.suggested_reorder_quantity,
                    model_name=result.model_name,
                    model_version=result.model_version,
                    confidence_score=result.confidence_score,
                    source_window_start=source_window_start,
                    source_window_end=source_window_end,
                    generated_at=result.generated_at,
                )
            )

        return forecasts

    async def get_forecast(self, forecast_id: UUID) -> Forecast:
        forecast = await self.forecast_repository.get_by_id(forecast_id)
        if forecast is None:
            raise NotFoundError("Forecast not found.")
        return forecast

    async def list_forecasts(
        self,
        *,
        product_id: UUID | None = None,
        status: str | None = None,
        period_start: date | None = None,
        period_end: date | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Forecast]:
        return await self.forecast_repository.list_filtered(
            product_id=product_id,
            status=status,
            period_start=period_start,
            period_end=period_end,
            search=search,
            offset=offset,
            limit=limit,
        )
