"""Scaffold module generated from `xpath_healer/rag/llm.py`."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

class LLM(ABC):
    """Prompt scaffold class preserving original members/signatures."""
    @abstractmethod
    async def suggest_locators(self, prompt_payload: dict[str, Any]) -> list[dict[str, Any]]:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: suggest_locators(self, prompt_payload: dict[str, Any]) -> list[dict[str, Any]]
        # TODO: Replace placeholder with a concrete `list[dict[str, Any]]` value.
        return None
