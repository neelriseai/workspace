"""Scaffold module generated from `xpath_healer/store/repository.py`."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Any

from xpath_healer.core.models import ElementMeta

class MetadataRepository(ABC):
    """Prompt scaffold for class `MetadataRepository` with original members/signatures."""
    @abstractmethod
    async def find(self, app_id: str, page_name: str, element_name: str) -> ElementMeta | None:
        """
        Prompt:
        Implement this method: `find(self, app_id: str, page_name: str, element_name: str) -> ElementMeta | None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @abstractmethod
    async def upsert(self, meta: ElementMeta) -> None:
        """
        Prompt:
        Implement this method: `upsert(self, meta: ElementMeta) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @abstractmethod
    async def find_candidates_by_page(self, app_id: str, page_name: str, field_type: str, limit: int = 25) -> list[ElementMeta]:
        """
        Prompt:
        Implement this method: `find_candidates_by_page(self, app_id: str, page_name: str, field_type: str, limit: int = 25) -> list[ElementMeta]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @abstractmethod
    async def log_event(self, event: dict[str, Any]) -> None:
        """
        Prompt:
        Implement this method: `log_event(self, event: dict[str, Any]) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
