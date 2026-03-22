# XPath Healer Master Design v3

## Objective
Provide deterministic-first locator healing with optional LLM/RAG assistance, using:
- PostgreSQL for durable metadata/events/page index.
- ChromaDB for vector retrieval.
- Playwright/Selenium adapters and FastAPI service entrypoint.

## High-level architecture
1. Core Layer
- Locator candidate construction, validation, scoring, strategy orchestration.

2. DB Layer
- Postgres tables for elements/page index/events.
- Chroma collections for semantic retrieval (`xh_rag_documents`, `xh_elements`).

3. Service/API Layer
- Facade initialization from env and stage flags.
- Dual repository behavior (Postgres primary + JSON fallback).

4. Model/RAG Layer
- OpenAI embedder + LLM.
- Chroma retriever for context candidates.

5. Testing/Automation Layer
- Integration scenarios for text box, checkbox, webtables, and negative raw fallback.

## Runtime flow (recover)
1. Receive broken fallback locator + context vars.
2. Execute enabled deterministic stages in order.
3. If still unresolved and RAG enabled, generate embedding, retrieve context via Chroma, query LLM, validate candidates.
4. Persist outcomes (metadata/events) and update retrievable context.

## Stage profiles
- `full`: deterministic + rag.
- `llm_only`: deterministic stages off, rag on.

## Non-goals
- Trust LLM output without validator checks.
- Replace deterministic recovery where deterministic evidence exists.
