# Service/API Layer Design v3

## Responsibilities
- Build facade runtime from env.
- Wire repository, validator, strategy context, and optional RAG stack.
- Expose a stable API for adapters and service endpoints.

## Main entrypoints
- `BaseHealerFacade`
- Adapter facades (`PlaywrightHealerFacade`, `SeleniumHealerFacade`)
- FastAPI service wrapper (`service/main.py`)

## Wiring behavior
- If `XH_PG_DSN` is set: use dual repository (Postgres primary + JSON fallback).
- If RAG enabled and API key valid: wire OpenAI embedder + OpenAI LLM + Chroma retriever.

## Stage toggles
- Controlled via `XH_STAGE_*` env flags.
- `XH_STAGE_PROFILE=llm_only` disables deterministic stages and keeps RAG active.
