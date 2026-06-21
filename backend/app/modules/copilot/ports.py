from typing import Protocol


class LLMProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        """Generate text through a future Phi-3 adapter."""


class RAGProvider(Protocol):
    async def answer(self, question: str) -> object:
        """Answer a question through a future retrieval adapter."""
