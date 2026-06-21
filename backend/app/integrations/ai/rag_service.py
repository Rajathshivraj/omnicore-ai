from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.integrations.ai.chroma_client import ChromaClient, RetrievedDocument
from app.integrations.ai.phi3_service import Phi3IntegrationService


@dataclass(frozen=True)
class RAGAnswer:
    answer: str
    source_refs: list[dict[str, Any]]
    model_name: str
    model_version: str


class RAGIntegrationService:
    """Retrieval augmented generation orchestration backed by ChromaDB and Phi-3."""

    def __init__(self, *, retriever: ChromaClient, llm: Phi3IntegrationService) -> None:
        self.retriever = retriever
        self.llm = llm

    async def answer(self, question: str, seed_documents: list[RetrievedDocument]) -> RAGAnswer:
        await self.retriever.upsert_documents(seed_documents)
        documents = await self.retriever.query(question, limit=5)
        if not documents:
            documents = seed_documents[:5]

        context = "\n\n".join(
            f"Source {index + 1}: {document.title}\n{document.content}"
            for index, document in enumerate(documents)
        )
        prompt = (
            "You are OmniCore AI's operations copilot. Answer with concise, "
            "auditable retail operations guidance. Do not claim to mutate data.\n\n"
            f"Question: {question}\n\nOperational context:\n{context}"
        )
        answer = await self.llm.complete(prompt)
        return RAGAnswer(
            answer=answer,
            source_refs=[
                {
                    "source_id": document.source_id,
                    "source_type": document.source_type,
                    "title": document.title,
                    "score": document.score,
                    "metadata": document.metadata,
                }
                for document in documents
            ],
            model_name=self.llm.model_name,
            model_version=self.llm.model_version,
        )
