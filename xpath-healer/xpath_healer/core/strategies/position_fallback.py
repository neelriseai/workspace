"""Scaffold module generated from `xpath_healer/core/strategies/position_fallback.py`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from xpath_healer.core.models import BuildInput, LocatorSpec

from xpath_healer.core.strategies.base import Strategy

from xpath_healer.utils.text import normalize_text

if TYPE_CHECKING:
    from xpath_healer.core.context import StrategyContext

class PositionFallbackStrategy(Strategy):
    """Prompt scaffold for class `PositionFallbackStrategy` with original members/signatures."""
    id = 'position_fallback'

    priority = 900

    stage = 'position'

    def supports(self, field_type: str, vars_map: dict[str, str]) -> bool:
        """
        Prompt:
        Implement this method: `supports(self, field_type: str, vars_map: dict[str, str]) -> bool`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def build(self, ctx: 'StrategyContext', inp: BuildInput) -> list[LocatorSpec]:
        """
        Prompt:
        Implement this method: `build(self, ctx: 'StrategyContext', inp: BuildInput) -> list[LocatorSpec]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
