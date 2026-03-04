"""Scaffold module generated from `xpath_healer/core/config.py`."""

from __future__ import annotations

import os

from dataclasses import asdict, dataclass, field

from xpath_healer.utils.text import coerce_bool

DEFAULT_ATTRIBUTE_PRIORITY = ['data-testid', 'aria-label', 'name', 'formcontrolname', 'placeholder', 'role', 'href', 'col-id', 'aria-colindex', 'class']

@dataclass(slots=True)
class ValidatorGeometryConfig:
    """Prompt scaffold for class `ValidatorGeometryConfig` with original members/signatures."""
    enabled: bool = True

    tolerance_px: float = 8.0

@dataclass(slots=True)
class ValidatorAxisConfig:
    """Prompt scaffold for class `ValidatorAxisConfig` with original members/signatures."""
    enabled: bool = True

@dataclass(slots=True)
class ValidatorConfig:
    """Prompt scaffold for class `ValidatorConfig` with original members/signatures."""
    require_visible: bool = True

    require_enabled_for_interactives: bool = True

    strict_single_match: bool = True

    geometry: ValidatorGeometryConfig = field(default_factory=ValidatorGeometryConfig)

    axis: ValidatorAxisConfig = field(default_factory=ValidatorAxisConfig)

@dataclass(slots=True)
class DomSnapshotConfig:
    """Prompt scaffold for class `DomSnapshotConfig` with original members/signatures."""
    cache_ttl_sec: int = 30

@dataclass(slots=True)
class StoreConfig:
    """Prompt scaffold for class `StoreConfig` with original members/signatures."""
    enabled: bool = True

    persist_events: bool = True

@dataclass(slots=True)
class RagConfig:
    """Prompt scaffold for class `RagConfig` with original members/signatures."""
    enabled: bool = False

    top_k: int = 5

@dataclass(slots=True)
class LoggingConfig:
    """Prompt scaffold for class `LoggingConfig` with original members/signatures."""
    level: str = 'INFO'

@dataclass(slots=True)
class HealerConfig:
    """Prompt scaffold for class `HealerConfig` with original members/signatures."""
    attribute_priority: list[str] = field(default_factory=lambda: list(DEFAULT_ATTRIBUTE_PRIORITY))

    similarity_threshold: float = 0.72

    allow_position_fallback: bool = False

    validator: ValidatorConfig = field(default_factory=ValidatorConfig)

    dom: DomSnapshotConfig = field(default_factory=DomSnapshotConfig)

    store: StoreConfig = field(default_factory=StoreConfig)

    rag: RagConfig = field(default_factory=RagConfig)

    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def to_dict(self) -> dict:
        """
        Prompt:
        Implement this method: `to_dict(self) -> dict`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")

    @classmethod
    def from_env(cls, prefix: str = 'XH_') -> HealerConfig:
        """
        Prompt:
        Implement this method: `from_env(cls, prefix: str = 'XH_') -> HealerConfig`.
        Keep the same arguments and return contract while recreating behavior.
        """
        raise NotImplementedError("Scaffold stub: implement based on the prompt above.")
