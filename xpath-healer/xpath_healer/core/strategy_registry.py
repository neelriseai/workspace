"""Scaffold module generated from `xpath_healer/core/strategy_registry.py`."""

from __future__ import annotations

from typing import Iterable

from xpath_healer.core.models import BuildInput, CandidateSpec

from xpath_healer.core.strategies.base import Strategy

class StrategyRegistry:
    """Prompt scaffold class preserving original members/signatures."""
    def __init__(self, strategies: Iterable[Strategy] | None = None) -> None:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: __init__(self, strategies: Iterable[Strategy] | None = None) -> None
        # Dependent call placeholders from original flow:
        # - self.register(strategy)
        # TODO: Initialize required instance attributes used by other methods.
        return None

    def register(self, strategy: Strategy) -> None:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: register(self, strategy: Strategy) -> None
        # Dependent call placeholders from original flow:
        # - self._strategies.append(strategy)
        # - self._strategies.sort(key=lambda s: s.priority)
        return None

    def ordered(self) -> list[Strategy]:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: ordered(self) -> list[Strategy]
        # TODO: Replace placeholder with a concrete `list[Strategy]` value.
        return None

    async def evaluate_all(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]:
        # Prompt: Implement this method keeping the same signature and return contract.
        # Signature: evaluate_all(self, ctx: 'StrategyContext', inp: BuildInput, allowed_stages: set[str] | None = None) -> list[CandidateSpec]
        # Dependent call placeholders from original flow:
        # - strategy.supports(inp.field_type, inp.vars)
        # - strategy.build(ctx, inp)
        # - locator.stable_hash()
        # - seen.add(key)
        # - candidates.append(CandidateSpec(strategy_id=strategy.id, locator=locator, stage=strategy.stage))
        # TODO: Replace placeholder with a concrete `list[CandidateSpec]` value.
        return None
