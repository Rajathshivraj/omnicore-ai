from datetime import date

import pytest

from app.integrations.ai.forecasting_service import (
    ForecastingInput,
    ForecastingIntegrationService,
    HistoricalDemandPoint,
)


@pytest.mark.asyncio
async def test_generate_forecast_uses_recent_demand_and_reorder_batches() -> None:
    provider = ForecastingIntegrationService()
    history = [
        HistoricalDemandPoint(demand_date=date(2026, 1, day), quantity=2)
        for day in range(1, 15)
    ] + [
        HistoricalDemandPoint(demand_date=date(2026, 1, day), quantity=4)
        for day in range(15, 29)
    ]

    result = await provider.generate(
        ForecastingInput(
            product_id="sku-1",
            current_available=20,
            reorder_point=5,
            reorder_quantity=10,
            forecast_period_start=date(2026, 2, 1),
            forecast_period_end=date(2026, 2, 10),
            history=history,
        )
    )

    assert result.predicted_demand > 0
    assert result.suggested_reorder_quantity >= 10
    assert result.model_version == "holt-linear-v1"


@pytest.mark.asyncio
async def test_generate_forecast_handles_missing_history() -> None:
    provider = ForecastingIntegrationService()

    result = await provider.generate(
        ForecastingInput(
            product_id="sku-1",
            current_available=12,
            reorder_point=4,
            reorder_quantity=None,
            forecast_period_start=date(2026, 2, 1),
            forecast_period_end=date(2026, 2, 7),
            history=[],
        )
    )

    assert result.predicted_demand == 0
    assert result.suggested_reorder_quantity == 0
    assert result.confidence_score == 35
