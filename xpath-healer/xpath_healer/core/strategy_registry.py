"""Scaffold module generated from `xpath_healer/core/strategy_registry.py`."""

from __future__ import annotations

from typing import Iterable

from xpath_healer.core.models import BuildInput, CandidateSpec

from xpath_healer.core.strategies.base import Strategy

class StrategyRegistry:
    """Prompt scaffold for class `StrategyRegistry` with original members/signatures."""
    def __init__(self, strategies: Iterable[Strategy] | None = None) -> None:
        """
        Prompt:
        Implement this method: `__init__(self, strategies: Iterable[Strategy] | None = None) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def register(self, strategy: Strategy) -> None:
        """
        Prompt:
        Implement this method: `register(self, strategy: Strategy) -> None`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    def ordered(self) -> list[Strategy]:
        """
        Prompt:
        Implement this method: `ordered(self) -> list[Strategy]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    async def evaluate_all(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]:
        """
        Prompt:
        Implement this method: `evaluate_all(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
