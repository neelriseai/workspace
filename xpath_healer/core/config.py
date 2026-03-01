"""Configuration for XPath healer."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field

from xpath_healer.utils.text import coerce_bool


DEFAULT_ATTRIBUTE_PRIORITY = [
    "data-testid",
    "aria-label",
    "name",
    "formcontrolname",
    "placeholder",
    "role",
    "href",
    "col-id",
    "aria-colindex",
    "class",
]


@dataclass(slots=True)
class ValidatorGeometryConfig:
    enabled: bool = True
    tolerance_px: float = 8.0


@dataclass(slots=True)
class ValidatorAxisConfig:
    enabled: bool = True


@dataclass(slots=True)
class ValidatorConfig:
    require_visible: bool = True
    require_enabled_for_interactives: bool = True
    strict_single_match: bool = True
    geometry: ValidatorGeometryConfig = field(default_factory=ValidatorGeometryConfig)
    axis: ValidatorAxisConfig = field(default_factory=ValidatorAxisConfig)


@dataclass(slots=True)
class DomSnapshotConfig:
    cache_ttl_sec: int = 30


@dataclass(slots=True)
class StoreConfig:
    enabled: bool = True
    persist_events: bool = True


@dataclass(slots=True)
class RagConfig:
    enabled: bool = False
    top_k: int = 5


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"


@dataclass(slots=True)
class HealerConfig:
    attribute_priority: list[str] = field(default_factory=lambda: list(DEFAULT_ATTRIBUTE_PRIORITY))
    similarity_threshold: float = 0.72
    allow_position_fallback: bool = False
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    dom: DomSnapshotConfig = field(default_factory=DomSnapshotConfig)
    store: StoreConfig = field(default_factory=StoreConfig)
    rag: RagConfig = field(default_factory=RagConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_env(cls, prefix: str = "XH_") -> HealerConfig:
        cfg = cls()

        attr_priority = os.getenv(f"{prefix}ATTRIBUTE_PRIORITY")
        if attr_priority:
            cfg.attribute_priority = [token.strip() for token in attr_priority.split(",") if token.strip()]

        similarity_threshold = os.getenv(f"{prefix}SIMILARITY_THRESHOLD")
        if similarity_threshold:
            cfg.similarity_threshold = float(similarity_threshold)

        allow_position = os.getenv(f"{prefix}ALLOW_POSITION_FALLBACK")
        if allow_position is not None:
            cfg.allow_position_fallback = coerce_bool(allow_position, cfg.allow_position_fallback)

        cfg.validator.require_visible = coerce_bool(
            os.getenv(f"{prefix}VALIDATOR_REQUIRE_VISIBLE"),
            cfg.validator.require_visible,
        )
        cfg.validator.require_enabled_for_interactives = coerce_bool(
            os.getenv(f"{prefix}VALIDATOR_REQUIRE_ENABLED"),
            cfg.validator.require_enabled_for_interactives,
        )
        cfg.validator.strict_single_match = coerce_bool(
            os.getenv(f"{prefix}VALIDATOR_STRICT_SINGLE_MATCH"),
            cfg.validator.strict_single_match,
        )
        cfg.validator.geometry.enabled = coerce_bool(
            os.getenv(f"{prefix}VALIDATOR_GEOMETRY_ENABLED"),
            cfg.validator.geometry.enabled,
        )
        tolerance = os.getenv(f"{prefix}VALIDATOR_GEOMETRY_TOLERANCE")
        if tolerance:
            cfg.validator.geometry.tolerance_px = float(tolerance)

        cfg.validator.axis.enabled = coerce_bool(
            os.getenv(f"{prefix}VALIDATOR_AXIS_ENABLED"),
            cfg.validator.axis.enabled,
        )

        cache_ttl = os.getenv(f"{prefix}DOM_CACHE_TTL_SEC")
        if cache_ttl:
            cfg.dom.cache_ttl_sec = int(cache_ttl)

        cfg.store.enabled = coerce_bool(os.getenv(f"{prefix}STORE_ENABLED"), cfg.store.enabled)
        cfg.store.persist_events = coerce_bool(os.getenv(f"{prefix}STORE_PERSIST_EVENTS"), cfg.store.persist_events)

        cfg.rag.enabled = coerce_bool(os.getenv(f"{prefix}RAG_ENABLED"), cfg.rag.enabled)
        rag_top_k = os.getenv(f"{prefix}RAG_TOP_K")
        if rag_top_k:
            cfg.rag.top_k = int(rag_top_k)

        level = os.getenv(f"{prefix}LOG_LEVEL")
        if level:
            cfg.logging.level = level.upper().strip()

        return cfg

