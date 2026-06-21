from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class HistoricalDemandPoint:
    demand_date: date
    quantity: int


@dataclass(frozen=True)
class ForecastingInput:
    product_id: str
    current_available: int
    reorder_point: int
    reorder_quantity: int | None
    forecast_period_start: date
    forecast_period_end: date
    history: Sequence[HistoricalDemandPoint]


@dataclass(frozen=True)
class ForecastingResult:
    predicted_demand: int
    suggested_reorder_quantity: int
    confidence_score: Decimal
    model_name: str
    model_version: str
    generated_at: datetime


class ForecastingIntegrationService:
    """Statistical demand forecasting adapter.

    This is a real deterministic forecasting implementation using Holt-style
    level/trend smoothing over daily demand. It is intentionally not labeled as
    LSTM; a trained LSTM runtime can replace this adapter behind the same
    service interface when model artifacts and training data exist.
    """

    def __init__(
        self,
        *,
        model_name: str = "statistical-demand-forecaster",
        model_version: str = "holt-linear-v1",
    ) -> None:
        self.model_name = model_name
        self.model_version = model_version

    async def generate(self, payload: ForecastingInput) -> ForecastingResult:
        horizon_days = max(
            (payload.forecast_period_end - payload.forecast_period_start).days + 1,
            1,
        )
        daily_demand = self._daily_demand(payload.history)
        predicted_demand = self._predict_demand(
            daily_demand=daily_demand,
            horizon_days=horizon_days,
        )
        coverage_gap = max(predicted_demand + payload.reorder_point - payload.current_available, 0)
        suggested_reorder_quantity = self._round_reorder_quantity(
            coverage_gap=coverage_gap,
            reorder_quantity=payload.reorder_quantity,
        )
        confidence_score = self._confidence_score(daily_demand)

        return ForecastingResult(
            predicted_demand=predicted_demand,
            suggested_reorder_quantity=suggested_reorder_quantity,
            confidence_score=confidence_score,
            model_name=self.model_name,
            model_version=self.model_version,
            generated_at=datetime.now(UTC),
        )

    def _daily_demand(self, history: Sequence[HistoricalDemandPoint]) -> list[int]:
        if not history:
            return []

        by_date: dict[date, int] = {}
        for point in history:
            by_date[point.demand_date] = by_date.get(point.demand_date, 0) + point.quantity

        start = min(by_date)
        end = max(by_date)
        days = (end - start).days + 1
        return [by_date.get(start + timedelta(days=offset), 0) for offset in range(days)]

    def _predict_demand(self, *, daily_demand: Sequence[int], horizon_days: int) -> int:
        if not daily_demand:
            return 0

        alpha = 0.45
        beta = 0.25
        level = float(daily_demand[0])
        trend = float(daily_demand[1] - daily_demand[0]) if len(daily_demand) > 1 else 0.0
        for demand in daily_demand[1:]:
            previous_level = level
            level = alpha * demand + (1 - alpha) * (level + trend)
            trend = beta * (level - previous_level) + (1 - beta) * trend

        forecast_values = [max(level + step * trend, 0) for step in range(1, horizon_days + 1)]
        return max(round(sum(forecast_values)), 0)

    def _round_reorder_quantity(self, *, coverage_gap: int, reorder_quantity: int | None) -> int:
        if coverage_gap <= 0:
            return 0
        if not reorder_quantity:
            return coverage_gap
        batches = (coverage_gap + reorder_quantity - 1) // reorder_quantity
        return batches * reorder_quantity

    def _confidence_score(self, daily_demand: Sequence[int]) -> Decimal:
        if not daily_demand:
            return Decimal("35.00")
        if len(daily_demand) < 14:
            return Decimal("55.00")
        avg = sum(daily_demand) / len(daily_demand)
        if avg == 0:
            return Decimal("60.00")
        variance = sum((value - avg) ** 2 for value in daily_demand) / len(daily_demand)
        volatility = min((variance**0.5) / avg, 1)
        confidence = 85 - (volatility * 30)
        return Decimal(str(round(max(confidence, 50), 2)))
