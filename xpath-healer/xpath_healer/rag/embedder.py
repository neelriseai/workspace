"""Scaffold module generated from `xpath_healer/rag/embedder.py`."""

from __future__ import annotations

from abc import ABC, abstractmethod

class Embedder(ABC):
    """Prompt scaffold for class `Embedder` with original members/signatures."""
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """
        Prompt:
        Implement this method: `embed_text(self, text: str) -> list[float]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
