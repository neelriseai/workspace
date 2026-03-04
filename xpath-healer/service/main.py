"""Scaffold module generated from `service/main.py`."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field

from xpath_healer.api.facade import XPathHealerFacade

from xpath_healer.core.models import HealingHints, LocatorSpec

class LocatorSpecModel(BaseModel):
    """Prompt scaffold for class `LocatorSpecModel` with original members/signatures."""
    kind: str

    value: str

    options: dict[str, Any] = Field(default_factory=dict)

    scope: 'LocatorSpecModel | None' = None

    def to_domain(self) -> LocatorSpec:
        """
        Prompt:
        Implement this method: `to_domain(self) -> LocatorSpec`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @classmethod
    def from_domain(cls, locator: LocatorSpec) -> 'LocatorSpecModel':
        """
        Prompt:
        Implement this method: `from_domain(cls, locator: LocatorSpec) -> 'LocatorSpecModel'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

LocatorSpecModel.model_rebuild()

class HealRequest(BaseModel):
    """Prompt scaffold for class `HealRequest` with original members/signatures."""
    app_id: str = 'default'

    page_name: str

    element_name: str

    field_type: str

    fallback: LocatorSpecModel

    vars: dict[str, str] = Field(default_factory=dict)

    hints: dict[str, Any] | None = None

    session_id: str | None = None

class GenerateRequest(BaseModel):
    """Prompt scaffold for class `GenerateRequest` with original members/signatures."""
    page_name: str

    element_name: str

    field_type: str

    vars: dict[str, str] = Field(default_factory=dict)

    hints: dict[str, Any] | None = None

def create_app(facade: XPathHealerFacade | None = None, page_resolver: Callable[[str], Awaitable[Any]] | None = None) -> FastAPI:
    """
    Prompt:
    Implement this function: `create_app(facade: XPathHealerFacade | None = None, page_resolver: Callable[[str], Awaitable[Any]] | None = None) -> FastAPI`.
    Keep the same arguments and return contract while recreating behavior.
    """
    raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

app = create_app()
