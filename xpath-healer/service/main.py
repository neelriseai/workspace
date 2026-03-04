"""Scaffold module generated from `service/main.py`."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field

from xpath_healer.api.facade import XPathHealerFacade

from xpath_healer.core.models import HealingHints, LocatorSpec

class LocatorSpecModel(BaseModel):
    """Prompt scaffold class preserving original members/signatures."""
    kind: str

    value: str

    options: dict[str, Any] = Field(default_factory=dict)

    scope: 'LocatorSpecModel | None' = None

    def to_domain(self) -> LocatorSpec:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: to_domain(self) -> LocatorSpec
        # Dependent call placeholders from original flow:
        # - self.scope.to_domain()
        # TODO: Replace placeholder with a concrete `LocatorSpec` value.
        return None

    @classmethod
    def from_domain(cls, locator: LocatorSpec) -> 'LocatorSpecModel':
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: from_domain(cls, locator: LocatorSpec) -> 'LocatorSpecModel'
        # Dependent call placeholders from original flow:
        # - cls.from_domain(locator.scope)
        # TODO: Replace placeholder with a concrete `'LocatorSpecModel'` value.
        return None

LocatorSpecModel.model_rebuild()

class HealRequest(BaseModel):
    """Prompt scaffold class preserving original members/signatures."""
    app_id: str = 'default'

    page_name: str

    element_name: str

    field_type: str

    fallback: LocatorSpecModel

    vars: dict[str, str] = Field(default_factory=dict)

    hints: dict[str, Any] | None = None

    session_id: str | None = None

class GenerateRequest(BaseModel):
    """Prompt scaffold class preserving original members/signatures."""
    page_name: str

    element_name: str

    field_type: str

    vars: dict[str, str] = Field(default_factory=dict)

    hints: dict[str, Any] | None = None

def create_app(facade: XPathHealerFacade | None = None, page_resolver: Callable[[str], Awaitable[Any]] | None = None) -> FastAPI:
    # Prompt: Implement this function keeping the same signature and return contract.
    # Signature: create_app(facade: XPathHealerFacade | None = None, page_resolver: Callable[[str], Awaitable[Any]] | None = None) -> FastAPI
    # Dependent call placeholders from original flow:
    # - app.get('/health')
    # - app.post('/generate')
    # - HealingHints.from_dict(req.hints)
    # - healer.generate_locator_async(page_name=req.page_name, element_name=req.element_name, field_type=req.field_type, vars=req.vars, hints=hints)
    # - LocatorSpecModel.from_domain(locator).model_dump()
    # - LocatorSpecModel.from_domain(locator)
    # TODO: Replace placeholder with a concrete `FastAPI` value.
    return None

app = create_app()
