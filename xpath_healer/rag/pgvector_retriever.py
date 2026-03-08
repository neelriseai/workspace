"""pgvector-backed retriever for RAG assist."""

from __future__ import annotations

import json
from typing import Any

from xpath_healer.rag.retriever import Retriever

try:
    import asyncpg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    asyncpg = None  # type: ignore[assignment]


class PgVectorRetriever(Retriever):
    def __init__(
        self,
        dsn: str,
        app_id: str = "",
        page_name: str = "",
        field_type: str = "",
        pool_min_size: int = 1,
        pool_max_size: int = 5,
    ) -> None:
        self.dsn = dsn
        self.app_id = app_id
        self.page_name = page_name
        self.field_type = field_type
        self.pool_min_size = max(1, int(pool_min_size))
        self.pool_max_size = max(self.pool_min_size, int(pool_max_size))
        self._pool: Any = None

    def set_query_context(self, app_id: str, page_name: str, field_type: str = "") -> None:
        self.app_id = app_id or ""
        self.page_name = page_name or ""
        self.field_type = field_type or ""

    async def connect(self) -> None:
        if self._pool is not None:
            return
        if asyncpg is None:
            raise RuntimeError("asyncpg is not installed. Install with: python -m pip install asyncpg")
        self._pool = await asyncpg.create_pool(  # type: ignore[union-attr]
            dsn=self.dsn,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
            command_timeout=30,
        )

    async def close(self) -> None:
        if self._pool is None:
            return
        await self._pool.close()
        self._pool = None

    async def retrieve(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        pool = await self._ensure_pool()
        vector_text = self._vector_literal(query_embedding)
        limit = max(1, int(top_k))

        async with pool.acquire() as conn:
            rows = await self._query_rag_documents(conn, vector_text, limit)
            if rows:
                return [self._row_to_rag_doc(row) for row in rows]

            rows = await self._query_elements(conn, vector_text, limit)
            return [self._row_to_element_candidate(row) for row in rows]

    async def _ensure_pool(self) -> Any:
        if self._pool is None:
            await self.connect()
        return self._pool

    async def _query_rag_documents(self, conn: Any, vector_text: str, limit: int) -> list[Any]:
        try:
            rows = await conn.fetch(
                """
                SELECT
                  app_id,
                  page_name,
                  element_name,
                  source,
                  chunk_text,
                  metadata,
                  1 - (embedding <=> $1::vector) AS similarity
                FROM rag_documents
                WHERE embedding IS NOT NULL
                  AND ($2 = '' OR app_id=$2)
                  AND ($3 = '' OR page_name=$3)
                  AND ($4 = '' OR coalesce(metadata->>'field_type','') = $4)
                ORDER BY embedding <=> $1::vector
                LIMIT $5
                """,
                vector_text,
                self.app_id,
                self.page_name,
                self.field_type,
                limit,
            )
        except Exception:
            return []
        return list(rows)

    async def _query_elements(self, conn: Any, vector_text: str, limit: int) -> list[Any]:
        try:
            rows = await conn.fetch(
                """
                SELECT
                  app_id,
                  page_name,
                  element_name,
                  field_type,
                  last_good_locator,
                  robust_locator,
                  signature,
                  quality_metrics,
                  1 - (signature_embedding <=> $1::vector) AS similarity
                FROM elements
                WHERE signature_embedding IS NOT NULL
                  AND ($2 = '' OR app_id=$2)
                  AND ($3 = '' OR page_name=$3)
                  AND ($4 = '' OR field_type=$4)
                ORDER BY signature_embedding <=> $1::vector
                LIMIT $5
                """,
                vector_text,
                self.app_id,
                self.page_name,
                self.field_type,
                limit,
            )
        except Exception:
            return []
        return list(rows)

    @staticmethod
    def _vector_literal(embedding: list[float]) -> str:
        values = [f"{float(value):.8f}" for value in embedding]
        return "[" + ",".join(values) + "]"

    @staticmethod
    def _decode_json(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return None
        return None

    def _row_to_rag_doc(self, row: Any) -> dict[str, Any]:
        metadata = self._decode_json(row.get("metadata")) or {}
        locator = metadata.get("locator") if isinstance(metadata, dict) else None
        out = {
            "app_id": row.get("app_id"),
            "page_name": row.get("page_name"),
            "element_name": row.get("element_name"),
            "source": row.get("source"),
            "chunk_text": row.get("chunk_text"),
            "metadata": metadata,
            "similarity": float(row.get("similarity") or 0.0),
        }
        if isinstance(locator, dict):
            out["locator"] = locator
        return out

    def _row_to_element_candidate(self, row: Any) -> dict[str, Any]:
        return {
            "app_id": row.get("app_id"),
            "page_name": row.get("page_name"),
            "element_name": row.get("element_name"),
            "field_type": row.get("field_type"),
            "last_good_locator": self._decode_json(row.get("last_good_locator")),
            "robust_locator": self._decode_json(row.get("robust_locator")),
            "signature": self._decode_json(row.get("signature")),
            "quality_metrics": self._decode_json(row.get("quality_metrics")) or {},
            "similarity": float(row.get("similarity") or 0.0),
        }
