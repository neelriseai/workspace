"""Scaffold module generated from `xpath_healer/rag/embedder.py`."""

from __future__ import annotations

from abc import ABC, abstractmethod

class Embedder(ABC):
    """Prompt scaffold class preserving original members/signatures."""
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: embed_text(self, text: str) -> list[float]
        # TODO: Replace placeholder with a concrete `list[float]` value.
        return None
