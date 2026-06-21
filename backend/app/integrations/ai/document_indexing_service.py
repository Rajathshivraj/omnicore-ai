from __future__ import annotations

from dataclasses import dataclass

from app.integrations.ai.chroma_client import ChromaClient, RetrievedDocument


@dataclass(frozen=True)
class DocumentToIndex:
    source_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, str]


class DocumentIndexingService:
    """Chunks operational documents and indexes them in ChromaDB."""

    def __init__(
        self,
        *,
        retriever: ChromaClient,
        chunk_size: int = 900,
        overlap: int = 120,
    ) -> None:
        self.retriever = retriever
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def index_documents(self, documents: list[DocumentToIndex]) -> int:
        chunks: list[RetrievedDocument] = []
        for document in documents:
            for index, chunk in enumerate(self._chunk_text(document.content)):
                chunks.append(
                    RetrievedDocument(
                        source_id=f"{document.source_id}:chunk:{index}",
                        source_type=document.source_type,
                        title=document.title,
                        content=chunk,
                        metadata={
                            **document.metadata,
                            "parent_source_id": document.source_id,
                            "chunk_index": str(index),
                        },
                    )
                )
        await self.retriever.upsert_documents(chunks)
        return len(chunks)

    def _chunk_text(self, content: str) -> list[str]:
        normalized = " ".join(content.split())
        if not normalized:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            chunks.append(normalized[start:end])
            if end == len(normalized):
                break
            start = max(end - self.overlap, start + 1)
        return chunks
