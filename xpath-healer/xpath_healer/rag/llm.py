"""Scaffold module generated from `xpath_healer/rag/llm.py`."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

class LLM(ABC):
    """Prompt scaffold for class `LLM` with original members/signatures."""
    @abstractmethod
    async def suggest_locators(self, prompt_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Prompt:
        Implement this method: `suggest_locators(self, prompt_payload: dict[str, Any]) -> list[dict[str, Any]]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
