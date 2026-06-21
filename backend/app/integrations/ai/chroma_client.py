from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class RetrievedDocument:
    source_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 0


class ChromaClient:
    """Small ChromaDB boundary with an in-process fallback for MVP RAG."""

    def __init__(
        self,
        *,
        endpoint_url: str | None = None,
        collection_name: str = "omnicore_operations",
    ) -> None:
        self.endpoint_url = endpoint_url
        self.collection_name = collection_name
        self._documents: list[RetrievedDocument] = []
        self._collection: Any | None = None

    async def upsert_documents(self, documents: list[RetrievedDocument]) -> None:
        collection = self._get_collection()
        if collection is not None:
            await asyncio.to_thread(self._upsert_chroma, collection, documents)
            return

        indexed = {document.source_id: document for document in self._documents}
        for document in documents:
            indexed[document.source_id] = document
        self._documents = list(indexed.values())

    async def query(self, question: str, *, limit: int = 5) -> list[RetrievedDocument]:
        collection = self._get_collection()
        if collection is not None:
            documents = await asyncio.to_thread(self._query_chroma, collection, question, limit)
            if documents:
                return documents

        terms = {term.lower() for term in question.split() if len(term) > 2}
        if not terms:
            return self._documents[:limit]

        scored: list[RetrievedDocument] = []
        for document in self._documents:
            searchable = f"{document.title} {document.content}".lower()
            score = sum(1 for term in terms if term in searchable)
            if score:
                scored.append(
                    RetrievedDocument(
                        source_id=document.source_id,
                        source_type=document.source_type,
                        title=document.title,
                        content=document.content,
                        metadata=document.metadata,
                        score=float(score),
                    )
                )
        return sorted(scored, key=lambda document: document.score, reverse=True)[:limit]

    def _get_collection(self) -> Any | None:
        if self._collection is not None:
            return self._collection
        if not self.endpoint_url:
            return None

        try:
            import chromadb
        except ImportError:
            return None

        endpoint_url = self.endpoint_url
        if "://" not in endpoint_url:
            endpoint_url = f"http://{endpoint_url}"

        parsed = urlparse(endpoint_url)
        host = parsed.hostname or self.endpoint_url
        if parsed.port:
            client = chromadb.HttpClient(host=host, port=parsed.port, ssl=parsed.scheme == "https")
        else:
            client = chromadb.HttpClient(host=host, ssl=parsed.scheme == "https")
        self._collection = client.get_or_create_collection(self.collection_name)
        return self._collection

    def _upsert_chroma(self, collection: Any, documents: list[RetrievedDocument]) -> None:
        if not documents:
            return
        collection.upsert(
            ids=[document.source_id for document in documents],
            documents=[document.content for document in documents],
            metadatas=[
                {
                    "source_type": document.source_type,
                    "title": document.title,
                    **document.metadata,
                }
                for document in documents
            ],
        )

    def _query_chroma(
        self,
        collection: Any,
        question: str,
        limit: int,
    ) -> list[RetrievedDocument]:
        result = collection.query(query_texts=[question], n_results=limit)
        ids = result.get("ids", [[]])[0]
        contents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if result.get("distances") else []
        documents: list[RetrievedDocument] = []
        for index, source_id in enumerate(ids):
            metadata = metadatas[index] or {}
            distance = distances[index] if index < len(distances) else 0
            documents.append(
                RetrievedDocument(
                    source_id=source_id,
                    source_type=metadata.pop("source_type", "operation"),
                    title=metadata.pop("title", source_id),
                    content=contents[index],
                    metadata=metadata,
                    score=float(1 / (1 + distance)),
                )
            )
        return documents
