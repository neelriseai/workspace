"""Scaffold module generated from `xpath_healer/utils/timing.py`."""

from __future__ import annotations

import time

from contextlib import contextmanager

from dataclasses import dataclass

from typing import Iterator

@dataclass(slots=True)
class Timing:
    """Prompt scaffold for class `Timing` with original members/signatures."""
    start: float

    end: float | None = None

    @property
    def elapsed_ms(self) -> float:
        """
        Prompt:
        Implement this method: `elapsed_ms(self) -> float`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

@contextmanager
def timed() -> Iterator[Timing]:
    """
    Prompt:
    Implement this function: `timed() -> Iterator[Timing]`.
    Keep the same arguments and return contract while recreating behavior.
    """
    raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
