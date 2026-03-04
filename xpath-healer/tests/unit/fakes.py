"""Scaffold module generated from `tests/unit/fakes.py`."""

from __future__ import annotations

import re

from dataclasses import dataclass, field

from typing import Any

from xpath_healer.utils.text import normalize_text

@dataclass
class FakeElement:
    """Prompt scaffold for class `FakeElement` with original members/signatures."""
    tag: str

    text: str = ''

    attrs: dict[str, str] = field(default_factory=dict)

    visible: bool = True

    enabled: bool = True

    bbox: dict[str, float] | None = None

    async def is_visible(self) -> bool:
        """
        Prompt:
        Implement this method: `is_visible(self) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def is_enabled(self) -> bool:
        """
        Prompt:
        Implement this method: `is_enabled(self) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def inner_text(self) -> str:
        """
        Prompt:
        Implement this method: `inner_text(self) -> str`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def bounding_box(self) -> dict[str, float] | None:
        """
        Prompt:
        Implement this method: `bounding_box(self) -> dict[str, float] | None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        """
        Prompt:
        Implement this method: `evaluate(self, script: str, arg: Any = None) -> Any`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def _html(self) -> str:
        """
        Prompt:
        Implement this method: `_html(self) -> str`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

class FakeLocator:
    """Prompt scaffold for class `FakeLocator` with original members/signatures."""
    def __init__(self, page: 'FakePage', elements: list[FakeElement]) -> None:
        """
        Prompt:
        Implement this method: `__init__(self, page: 'FakePage', elements: list[FakeElement]) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def count(self) -> int:
        """
        Prompt:
        Implement this method: `count(self) -> int`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def nth(self, idx: int) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `nth(self, idx: int) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @property
    def first(self) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `first(self) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @property
    def last(self) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `last(self) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def filter(self, has_text: str | None = None) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `filter(self, has_text: str | None = None) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def locator(self, selector: str) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `locator(self, selector: str) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def get_by_text(self, text: str, exact: bool = False) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `get_by_text(self, text: str, exact: bool = False) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def get_by_role(self, role: str, **kwargs: Any) -> 'FakeLocator':
        """
        Prompt:
        Implement this method: `get_by_role(self, role: str, **kwargs: Any) -> 'FakeLocator'`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def is_visible(self) -> bool:
        """
        Prompt:
        Implement this method: `is_visible(self) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def is_enabled(self) -> bool:
        """
        Prompt:
        Implement this method: `is_enabled(self) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def inner_text(self) -> str:
        """
        Prompt:
        Implement this method: `inner_text(self) -> str`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        """
        Prompt:
        Implement this method: `evaluate(self, script: str, arg: Any = None) -> Any`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def bounding_box(self) -> dict[str, float] | None:
        """
        Prompt:
        Implement this method: `bounding_box(self) -> dict[str, float] | None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

class FakePage:
    """Prompt scaffold for class `FakePage` with original members/signatures."""
    def __init__(self) -> None:
        """
        Prompt:
        Implement this method: `__init__(self) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def add_element(self, element: FakeElement, selectors: list[str] | None = None) -> None:
        """
        Prompt:
        Implement this method: `add_element(self, element: FakeElement, selectors: list[str] | None = None) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def register_selector(self, selector: str, elements: list[FakeElement]) -> None:
        """
        Prompt:
        Implement this method: `register_selector(self, selector: str, elements: list[FakeElement]) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def locator(self, selector: str) -> FakeLocator:
        """
        Prompt:
        Implement this method: `locator(self, selector: str) -> FakeLocator`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def get_by_text(self, text: str, exact: bool = False) -> FakeLocator:
        """
        Prompt:
        Implement this method: `get_by_text(self, text: str, exact: bool = False) -> FakeLocator`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def get_by_role(self, role: str, **kwargs: Any) -> FakeLocator:
        """
        Prompt:
        Implement this method: `get_by_role(self, role: str, **kwargs: Any) -> FakeLocator`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        """
        Prompt:
        Implement this method: `evaluate(self, script: str, arg: Any = None) -> Any`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def _html(self) -> str:
        """
        Prompt:
        Implement this method: `_html(self) -> str`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @staticmethod
    def _tag_matches_role(element: FakeElement, expected_role: str) -> bool:
        """
        Prompt:
        Implement this method: `_tag_matches_role(element: FakeElement, expected_role: str) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def _match_css(self, selector: str) -> list[FakeElement]:
        """
        Prompt:
        Implement this method: `_match_css(self, selector: str) -> list[FakeElement]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def _match_css_part(self, part: str) -> list[FakeElement]:
        """
        Prompt:
        Implement this method: `_match_css_part(self, part: str) -> list[FakeElement]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
