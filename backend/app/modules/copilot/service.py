from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.errors import BusinessRuleError, NotFoundError
from app.db.enums import AIInsightType, ReviewStatus
from app.integrations.ai.chroma_client import RetrievedDocument
from app.integrations.ai.rag_service import RAGIntegrationService
from app.modules.copilot.models import AIInsight
from app.modules.copilot.repository import AIInsightRepository
from app.modules.forecasting.repository import ForecastRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository


class AIInsightService:
    """Coordinates AI insight persistence and recommendation review workflows."""

    def __init__(self, ai_insight_repository: AIInsightRepository) -> None:
        self.ai_insight_repository = ai_insight_repository

    async def get_insight(self, insight_id: UUID) -> AIInsight:
        insight = await self.ai_insight_repository.get_by_id(insight_id)
        if insight is None:
            raise NotFoundError("AI insight not found.")
        return insight

    async def list_insights(
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
    ) -> Sequence[AIInsight]:
        return await self.ai_insight_repository.list_filtered(
            insight_type=insight_type,
            status=status,
            product_id=product_id,
            order_id=order_id,
            forecast_id=forecast_id,
            reviewed_by_id=reviewed_by_id,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def store_recommendation(
        self,
        *,
        title: str,
        summary: str,
        suggested_action: str | None = None,
        confidence_score: Decimal | None = None,
        product_id: UUID | None = None,
        order_id: UUID | None = None,
        forecast_id: UUID | None = None,
        source_refs: list[dict[str, Any]] | None = None,
        input_snapshot: dict[str, Any] | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        generated_at: datetime | None = None,
    ) -> AIInsight:
        if product_id is None and order_id is None and forecast_id is None:
            raise BusinessRuleError(
                "AI recommendation must reference product, order, or forecast context."
            )
        if confidence_score is not None and not Decimal("0") <= confidence_score <= Decimal("100"):
            raise BusinessRuleError("AI recommendation confidence score must be between 0 and 100.")

        return await self.ai_insight_repository.create(
            {
                "insight_type": AIInsightType.RECOMMENDATION,
                "status": ReviewStatus.NEW,
                "title": title,
                "summary": summary,
                "suggested_action": suggested_action,
                "confidence_score": confidence_score,
                "product_id": product_id,
                "order_id": order_id,
                "forecast_id": forecast_id,
                "source_refs": source_refs or [],
                "input_snapshot": input_snapshot or {},
                "model_name": model_name,
                "model_version": model_version,
                "generated_at": generated_at or datetime.now(UTC),
            }
        )

    async def store_answer(
        self,
        *,
        title: str,
        summary: str,
        source_refs: list[dict[str, Any]],
        input_snapshot: dict[str, Any],
        suggested_action: str | None = None,
        confidence_score: Decimal | None = None,
        product_id: UUID | None = None,
        order_id: UUID | None = None,
        forecast_id: UUID | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        generated_at: datetime | None = None,
    ) -> AIInsight:
        if confidence_score is not None and not Decimal("0") <= confidence_score <= Decimal("100"):
            raise BusinessRuleError("AI answer confidence score must be between 0 and 100.")

        return await self.ai_insight_repository.create(
            {
                "insight_type": AIInsightType.RAG_ANSWER,
                "status": ReviewStatus.NEW,
                "title": title,
                "summary": summary,
                "suggested_action": suggested_action,
                "confidence_score": confidence_score,
                "product_id": product_id,
                "order_id": order_id,
                "forecast_id": forecast_id,
                "source_refs": source_refs,
                "input_snapshot": input_snapshot,
                "model_name": model_name,
                "model_version": model_version,
                "generated_at": generated_at or datetime.now(UTC),
            }
        )


class CopilotService(AIInsightService):
    """Operations copilot backed by RAG and persisted through AIInsight."""

    def __init__(
        self,
        *,
        ai_insight_repository: AIInsightRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
        order_repository: OrderRepository,
        forecast_repository: ForecastRepository,
        rag_provider: RAGIntegrationService,
    ) -> None:
        super().__init__(ai_insight_repository=ai_insight_repository)
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.order_repository = order_repository
        self.forecast_repository = forecast_repository
        self.rag_provider = rag_provider

    async def answer_question(self, question: str) -> AIInsight:
        normalized = question.lower()
        documents = await self._build_context_documents()
        deterministic_answer = self._answer_from_operational_context(normalized, documents)
        rag_answer = await self.rag_provider.answer(
            question=question,
            seed_documents=[
                *documents,
                RetrievedDocument(
                    source_id="copilot:deterministic-summary",
                    source_type="copilot_analysis",
                    title="Deterministic operations analysis",
                    content=deterministic_answer,
                ),
            ],
        )
        summary = deterministic_answer
        if rag_answer.answer and "not configured" not in rag_answer.answer.lower():
            summary = rag_answer.answer

        context = self._primary_context(rag_answer.source_refs)
        return await self.store_answer(
            title=question[:200],
            summary=summary,
            suggested_action=self._suggested_action(normalized),
            confidence_score=Decimal("78.00"),
            product_id=context.get("product_id"),
            forecast_id=context.get("forecast_id"),
            source_refs=rag_answer.source_refs,
            input_snapshot={"question": question, "documents_considered": len(documents)},
            model_name=rag_answer.model_name,
            model_version=rag_answer.model_version,
        )

    async def _build_context_documents(self) -> list[RetrievedDocument]:
        product_records = await self.product_repository.list_filtered(limit=100)
        products = {product.id: product for product in product_records}
        inventory_records = await self.inventory_repository.list_filtered(limit=100)
        forecasts = await self.forecast_repository.list_filtered(limit=100)
        orders = await self.order_repository.list_filtered(limit=200)

        documents: list[RetrievedDocument] = []
        for inventory in inventory_records:
            product = products.get(inventory.product_id)
            product_name = product.name if product else str(inventory.product_id)
            documents.append(
                RetrievedDocument(
                    source_id=f"inventory:{inventory.id}",
                    source_type="inventory",
                    title=f"Inventory risk for {product_name}",
                    content=(
                        f"{product_name} has {inventory.stock_available} available units at "
                        f"{inventory.location_code}, reorder point {inventory.reorder_point}, "
                        f"reorder quantity {inventory.reorder_quantity}, status "
                        f"{inventory.inventory_status}."
                    ),
                    metadata={"product_id": str(inventory.product_id)},
                )
            )
        for forecast in forecasts:
            product = products.get(forecast.product_id)
            product_name = product.name if product else str(forecast.product_id)
            documents.append(
                RetrievedDocument(
                    source_id=f"forecast:{forecast.id}",
                    source_type="forecast",
                    title=f"Demand forecast for {product_name}",
                    content=(
                        f"{product_name} forecast demand is {forecast.predicted_demand} "
                        f"from {forecast.forecast_period_start} to {forecast.forecast_period_end}; "
                        f"suggested reorder is {forecast.suggested_reorder_quantity}, "
                        f"confidence {forecast.confidence_score}, model {forecast.model_version}."
                    ),
                    metadata={
                        "product_id": str(forecast.product_id),
                        "forecast_id": str(forecast.id),
                    },
                )
            )
        documents.append(self._sales_document(orders))
        return documents

    def _sales_document(self, orders: Sequence[Any]) -> RetrievedDocument:
        now = datetime.now(UTC)
        recent_revenue = Decimal("0")
        previous_revenue = Decimal("0")
        recent_units = 0
        previous_units = 0
        for order in orders:
            placed_at = order.placed_at
            if placed_at.tzinfo is None:
                placed_at = placed_at.replace(tzinfo=UTC)
            days_old = (now - placed_at).days
            if 0 <= days_old < 30:
                recent_revenue += order.total_amount
                recent_units += sum(item.quantity for item in order.items)
            elif 30 <= days_old < 60:
                previous_revenue += order.total_amount
                previous_units += sum(item.quantity for item in order.items)
        revenue_delta = recent_revenue - previous_revenue
        unit_delta = recent_units - previous_units
        return RetrievedDocument(
            source_id="analytics:sales-window",
            source_type="analytics",
            title="Sales trend comparison",
            content=(
                f"Last 30 days revenue {recent_revenue} versus prior 30 days "
                f"{previous_revenue}; revenue delta {revenue_delta}. Last 30 days "
                f"units {recent_units} versus prior units {previous_units}; "
                f"unit delta {unit_delta}."
            ),
        )

    def _answer_from_operational_context(
        self,
        normalized_question: str,
        documents: Sequence[RetrievedDocument],
    ) -> str:
        if "sales" in normalized_question and (
            "down" in normalized_question or "why" in normalized_question
        ):
            sales = next(
                document for document in documents if document.source_id == "analytics:sales-window"
            )
            risk = [
                document
                for document in documents
                if document.source_type in {"inventory", "forecast"}
            ][:3]
            return (
                f"{sales.content} Likely drivers to inspect are stock coverage, forecasted demand, "
                f"and replenishment gaps. Supporting signals: "
                f"{'; '.join(document.content for document in risk)}"
            )
        if "reorder" in normalized_question:
            candidates = [
                document.content
                for document in documents
                if "suggested reorder is 0" not in document.content
                and document.source_type == "forecast"
            ][:5]
            details = "; ".join(candidates) if candidates else "No forecasted reorder need found."
            return f"Products to reorder: {details}"
        if "risk" in normalized_question or "at risk" in normalized_question:
            candidates = [
                document.content
                for document in documents
                if "stockout" in document.content.lower()
                or "low_stock" in document.content.lower()
                or "suggested reorder is 0" not in document.content
            ][:5]
            details = "; ".join(candidates) if candidates else "No current risk signals found."
            return f"Inventory at risk: {details}"
        return (
            "I reviewed sales, inventory, and forecast context. Prioritize low available stock, "
            "positive reorder suggestions, and recent sales changes before taking action."
        )

    def _suggested_action(self, normalized_question: str) -> str:
        if "reorder" in normalized_question:
            return (
                "Review replenishment suggestions and approve purchase quantities "
                "for constrained SKUs."
            )
        if "risk" in normalized_question:
            return (
                "Review stockout-risk SKUs and confirm inventory counts before "
                "changing allocations."
            )
        if "sales" in normalized_question:
            return (
                "Compare recent demand, stock availability, and fulfillment "
                "exceptions before changing plans."
            )
        return "Review the cited operational sources before approving any critical action."

    def _primary_context(self, source_refs: Sequence[dict[str, Any]]) -> dict[str, UUID]:
        for source_ref in source_refs:
            metadata = source_ref.get("metadata") or {}
            context: dict[str, UUID] = {}
            if metadata.get("product_id"):
                context["product_id"] = UUID(metadata["product_id"])
            if metadata.get("forecast_id"):
                context["forecast_id"] = UUID(metadata["forecast_id"])
            if context:
                return context
        return {}
