"""Scaffold module generated from `xpath_healer/core/exceptions.py`."""

from __future__ import annotations

from dataclasses import dataclass

from xpath_healer.core.models import StrategyTrace

class XPathHealerError(Exception):
    """Prompt scaffold for class `XPathHealerError` with original members/signatures."""

@dataclass(slots=True)
class RecoveryFailed(XPathHealerError):
    """Prompt scaffold for class `RecoveryFailed` with original members/signatures."""
    message: str

    correlation_id: str

    trace: list[StrategyTrace]

    def __str__(self) -> str:
        """
        Prompt:
        Implement this method: `__str__(self) -> str`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
