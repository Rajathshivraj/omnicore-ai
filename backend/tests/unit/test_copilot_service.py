from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.integrations.ai.rag_service import RAGAnswer
from app.modules.copilot.service import CopilotService


class FakeAIInsightRepository:
    def __init__(self) -> None:
        self.created: dict | None = None

    async def create(self, data: dict) -> SimpleNamespace:
        self.created = data
        return SimpleNamespace(id=uuid4(), **data)


class FakeRAGProvider:
    async def answer(self, question: str, seed_documents: list) -> RAGAnswer:
        return RAGAnswer(
            answer="Model inference is not configured.",
            source_refs=[
                {
                    "source_id": "analytics:sales-window",
                    "source_type": "analytics",
                    "title": "Sales trend comparison",
                    "score": 1,
                    "metadata": {},
                }
            ],
            model_name="phi-3",
            model_version="local",
        )


class FakeProductRepository:
    async def list_filtered(self, **_: object) -> list:
        return []


class FakeInventoryRepository:
    async def list_filtered(self, **_: object) -> list:
        return []


class FakeForecastRepository:
    async def list_filtered(self, **_: object) -> list:
        return []


class FakeOrderRepository:
    async def list_filtered(self, **_: object) -> list:
        return [
            SimpleNamespace(
                placed_at=datetime.now(UTC) - timedelta(days=5),
                total_amount=Decimal("100.00"),
                items=[SimpleNamespace(quantity=3)],
            ),
            SimpleNamespace(
                placed_at=datetime.now(UTC) - timedelta(days=35),
                total_amount=Decimal("180.00"),
                items=[SimpleNamespace(quantity=6)],
            ),
        ]


@pytest.mark.asyncio
async def test_copilot_persists_sales_question_as_ai_insight() -> None:
    ai_repo = FakeAIInsightRepository()
    service = CopilotService(
        ai_insight_repository=ai_repo,
        product_repository=FakeProductRepository(),
        inventory_repository=FakeInventoryRepository(),
        order_repository=FakeOrderRepository(),
        forecast_repository=FakeForecastRepository(),
        rag_provider=FakeRAGProvider(),
    )

    insight = await service.answer_question("Why are sales down?")

    assert insight.insight_type == "rag_answer"
    assert insight.input_snapshot["question"] == "Why are sales down?"
    assert "revenue delta -80.00" in insight.summary
    assert ai_repo.created is not None
