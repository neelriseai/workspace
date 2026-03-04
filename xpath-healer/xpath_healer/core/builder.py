"""Scaffold module generated from `xpath_healer/core/builder.py`."""

from __future__ import annotations

from xpath_healer.core.models import BuildInput, CandidateSpec

from xpath_healer.core.strategy_registry import StrategyRegistry

class XPathBuilder:
    """Prompt scaffold for class `XPathBuilder` with original members/signatures."""
    def __init__(self, registry: StrategyRegistry) -> None:
        """
        Prompt:
        Implement this method: `__init__(self, registry: StrategyRegistry) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def build_all_candidates(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]:
        """
        Prompt:
        Implement this method: `build_all_candidates(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
