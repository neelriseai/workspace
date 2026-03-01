"""PostgreSQL repository skeleton (Phase B implementation target)."""

from __future__ import annotations

from typing import Any

from xpath_healer.core.models import ElementMeta
from xpath_healer.store.repository import MetadataRepository


class PostgresMetadataRepository(MetadataRepository):
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    async def find(self, app_id: str, page_name: str, element_name: str) -> ElementMeta | None:
        raise NotImplementedError("Phase B: implement Postgres repository.")

    async def upsert(self, meta: ElementMeta) -> None:
        raise NotImplementedError("Phase B: implement Postgres repository.")

    async def find_candidates_by_page(
        self,
        app_id: str,
        page_name: str,
        field_type: str,
        limit: int = 25,
    ) -> list[ElementMeta]:
        raise NotImplementedError("Phase B: implement Postgres repository.")

    async def log_event(self, event: dict[str, Any]) -> None:
        raise NotImplementedError("Phase B: implement event store.")

    @staticmethod
    def schema_sql() -> str:
        return """
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS elements (
          id uuid PRIMARY KEY,
          app_id text NOT NULL,
          page_name text NOT NULL,
          element_name text NOT NULL,
          field_type text NOT NULL,
          last_good_locator jsonb,
          robust_locator jsonb,
          strategy_id text,
          signature jsonb,
          signature_embedding vector(1536),
          hints jsonb,
          last_seen timestamptz NOT NULL DEFAULT now(),
          success_count int NOT NULL DEFAULT 0,
          fail_count int NOT NULL DEFAULT 0,
          UNIQUE(app_id, page_name, element_name)
        );

        CREATE TABLE IF NOT EXISTS events (
          id bigserial PRIMARY KEY,
          correlation_id text NOT NULL,
          timestamp timestamptz NOT NULL DEFAULT now(),
          app_id text,
          page_name text,
          element_name text,
          field_type text,
          stage text,
          status text,
          score double precision,
          details jsonb
        );
        """

