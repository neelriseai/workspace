# DB Layer Design v3 (PostgreSQL + ChromaDB)

## Responsibilities
- Persist structured metadata and event logs in Postgres.
- Persist/retrieve vectorized context through ChromaDB.

## Postgres scope
- Tables: `elements`, `page_index`, `indexed_elements`, `locator_variants`, `quality_metrics`, `events`, `healing_events`, `rag_documents`.
- `rag_documents` stores chunk text + metadata (no pgvector column in v3 schema).

## Chroma scope
- Collections:
  - `xh_rag_documents`
  - `xh_elements`
- Used for nearest-neighbor retrieval in RAG flows.

## Key guarantees
- Metadata CRUD and event persistence remain available even if Chroma is unavailable.
- Vector writes are best-effort and do not replace authoritative metadata persistence.

## Env controls
- `XH_PG_DSN`, `XH_PG_POOL_MIN`, `XH_PG_POOL_MAX`, `XH_PG_AUTO_INIT_SCHEMA`
- `XH_CHROMA_PATH`, `XH_CHROMA_RAG_COLLECTION`, `XH_CHROMA_ELEMENTS_COLLECTION`
