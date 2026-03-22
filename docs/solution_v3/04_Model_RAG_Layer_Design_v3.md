# Model/RAG Layer Design v3

## Responsibilities
- Build compact query from request + DOM signature.
- Retrieve semantic context from ChromaDB.
- Ask LLM for candidate locators.
- Re-rank and validate candidates before acceptance.

## Components
- `OpenAIEmbedder`
- `ChromaRetriever`
- `OpenAILLM`
- `RagAssist`

## Guardrails
- Candidate de-duplication.
- Anti-hallucination checks (grounding, red flags, confidence threshold).
- Validator is final authority for accept/reject.

## Telemetry
- `rag_context` metrics include context counts, prompt sizes, embedding dimensions, and compression ratio.
