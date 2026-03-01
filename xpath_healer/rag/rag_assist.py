"""Optional RAG stage that proposes locator specs (must be validated)."""

from __future__ import annotations

from typing import Any

from xpath_healer.core.models import BuildInput, LocatorSpec
from xpath_healer.rag.embedder import Embedder
from xpath_healer.rag.llm import LLM
from xpath_healer.rag.retriever import Retriever


class RagAssist:
    def __init__(self, embedder: Embedder, retriever: Retriever, llm: LLM) -> None:
        self.embedder = embedder
        self.retriever = retriever
        self.llm = llm

    async def suggest(self, inp: BuildInput, dom_snippet: str, top_k: int = 5) -> list[LocatorSpec]:
        query = self._build_query(inp, dom_snippet)
        embedding = await self.embedder.embed_text(query)
        context = await self.retriever.retrieve(embedding, top_k=top_k)
        payload = {
            "task": "suggest_locator_specs",
            "field_type": inp.field_type,
            "intent": inp.intent.to_dict(),
            "vars": inp.vars,
            "dom_snippet": dom_snippet[:15000],
            "context": context,
            "rules": {
                "no_absolute_xpath_with_deep_indices": True,
                "output_schema": {"kind": "css|xpath|role|text|pw", "value": "string", "options": "object"},
            },
        }
        raw = await self.llm.suggest_locators(payload)
        return self._parse_suggestions(raw)

    @staticmethod
    def _build_query(inp: BuildInput, dom_snippet: str) -> str:
        return (
            f"page={inp.page_name}; element={inp.element_name}; field_type={inp.field_type}; "
            f"vars={inp.vars}; dom={dom_snippet[:2000]}"
        )

    @staticmethod
    def _parse_suggestions(raw: list[dict[str, Any]]) -> list[LocatorSpec]:
        out: list[LocatorSpec] = []
        for item in raw:
            try:
                out.append(
                    LocatorSpec(
                        kind=str(item["kind"]),
                        value=str(item["value"]),
                        options=dict(item.get("options") or {}),
                        scope=LocatorSpec.from_dict(item["scope"]) if item.get("scope") else None,
                    )
                )
            except Exception:
                continue
        return out

