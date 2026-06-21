from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.config import Settings, get_settings
from app.core.dependencies import DbSession
from app.integrations.ai.chroma_client import ChromaClient
from app.integrations.ai.document_indexing_service import DocumentIndexingService, DocumentToIndex
from app.integrations.ai.phi3_service import Phi3IntegrationService
from app.integrations.ai.rag_service import RAGIntegrationService
from app.modules.auth.dependencies import require_permissions
from app.modules.copilot.repository import AIInsightRepository
from app.modules.copilot.schemas import (
    AIInsightCreateRequest,
    AIInsightListResponse,
    AIInsightResponse,
    CopilotAskRequest,
    KnowledgeIndexRequest,
    KnowledgeIndexResponse,
)
from app.modules.copilot.service import AIInsightService, CopilotService
from app.modules.forecasting.repository import ForecastRepository
from app.modules.inventory.repository import InventoryRepository
from app.modules.orders.repository import OrderRepository
from app.modules.products.repository import ProductRepository
from app.modules.shared.permissions import Permission
from app.modules.users.models import User
from app.schemas.pagination import PageMeta

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])


async def get_ai_insight_service(session: DbSession) -> AIInsightService:
    return AIInsightService(ai_insight_repository=AIInsightRepository(session))


async def get_copilot_service(
    session: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> CopilotService:
    llm = Phi3IntegrationService(
        endpoint_url=settings.phi3_endpoint_url,
        model_name=settings.phi3_model_name,
        model_version=settings.phi3_model_version,
    )
    retriever = ChromaClient(
        endpoint_url=settings.chroma_endpoint_url,
        collection_name=settings.chroma_collection_name,
    )
    return CopilotService(
        ai_insight_repository=AIInsightRepository(session),
        product_repository=ProductRepository(session),
        inventory_repository=InventoryRepository(session),
        order_repository=OrderRepository(session),
        forecast_repository=ForecastRepository(session),
        rag_provider=RAGIntegrationService(retriever=retriever, llm=llm),
    )


AIInsightServiceDep = Annotated[AIInsightService, Depends(get_ai_insight_service)]
CopilotServiceDep = Annotated[CopilotService, Depends(get_copilot_service)]


async def get_document_indexing_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentIndexingService:
    return DocumentIndexingService(
        retriever=ChromaClient(
            endpoint_url=settings.chroma_endpoint_url,
            collection_name=settings.chroma_collection_name,
        )
    )


DocumentIndexingServiceDep = Annotated[
    DocumentIndexingService,
    Depends(get_document_indexing_service),
]


@router.get(
    "",
    response_model=AIInsightListResponse,
    summary="List AI insights",
    description=(
        "Returns paginated AI recommendation and insight records with context "
        "and review filters."
    ),
)
async def list_ai_insights(
    service: AIInsightServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_AI_INSIGHTS))],
    insight_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    product_id: UUID | None = Query(default=None),
    order_id: UUID | None = Query(default=None),
    forecast_id: UUID | None = Query(default=None),
    reviewed_by_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> AIInsightListResponse:
    items = await service.list_insights(
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
    return AIInsightListResponse(
        items=list(items),
        meta=PageMeta(offset=offset, limit=limit, count=len(items)),
    )


@router.post(
    "",
    response_model=AIInsightResponse,
    status_code=201,
    summary="Store AI recommendation",
    description="Stores an AI recommendation record. This does not execute model inference.",
)
async def create_ai_insight(
    payload: AIInsightCreateRequest,
    service: AIInsightServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.REVIEW_AI_INSIGHTS))],
) -> object:
    insight = await service.store_recommendation(**payload.model_dump())
    await session.commit()
    return insight


@router.post(
    "/ask",
    response_model=AIInsightResponse,
    status_code=201,
    summary="Ask operations copilot",
    description=(
        "Answers an operations question through RAG and persists the answer "
        "as an AIInsight."
    ),
)
async def ask_copilot(
    payload: CopilotAskRequest,
    service: CopilotServiceDep,
    session: DbSession,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_AI_INSIGHTS))],
) -> object:
    insight = await service.answer_question(payload.question)
    await session.commit()
    return insight


@router.post(
    "/knowledge/index",
    response_model=KnowledgeIndexResponse,
    status_code=201,
    summary="Index operational knowledge",
)
async def index_knowledge(
    payload: KnowledgeIndexRequest,
    service: DocumentIndexingServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.REVIEW_AI_INSIGHTS))],
) -> KnowledgeIndexResponse:
    indexed_chunks = await service.index_documents(
        [
            DocumentToIndex(
                source_id=document.source_id,
                source_type=document.source_type,
                title=document.title,
                content=document.content,
                metadata=document.metadata,
            )
            for document in payload.documents
        ]
    )
    return KnowledgeIndexResponse(indexed_chunks=indexed_chunks)


@router.get("/{insight_id}", response_model=AIInsightResponse, summary="Get AI insight")
async def get_ai_insight(
    insight_id: UUID,
    service: AIInsightServiceDep,
    _: Annotated[User, Depends(require_permissions(Permission.VIEW_AI_INSIGHTS))],
) -> object:
    return await service.get_insight(insight_id)
