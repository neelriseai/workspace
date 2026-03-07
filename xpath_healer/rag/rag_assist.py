"""Optional RAG stage that proposes locator specs (must be validated)."""

from __future__ import annotations

from typing import Any

from xpath_healer.core.models import BuildInput, LocatorSpec
from xpath_healer.rag.embedder import Embedder
from xpath_healer.rag.llm import LLM
from xpath_healer.rag.prompt_builder import build_prompt_payload
from xpath_healer.rag.retriever import Retriever


class RagAssist:
    def __init__(self, embedder: Embedder, retriever: Retriever, llm: LLM) -> None:
        self.embedder = embedder
        self.retriever = retriever
        self.llm = llm

    async def suggest(self, inp: BuildInput, dom_snippet: str, top_k: int = 5) -> list[LocatorSpec]:
        query = self._build_query(inp, dom_snippet)
        embedding = await self.embedder.embed_text(query)
        if hasattr(self.retriever, "set_query_context"):
            try:
                self.retriever.set_query_context(  # type: ignore[attr-defined]
                    app_id=inp.app_id,
                    page_name=inp.page_name,
                    field_type=inp.field_type,
                )
            except Exception:
                pass
        retrieve_k = min(max(top_k * 20, 50), 200)
        raw_context = await self.retriever.retrieve(embedding, top_k=retrieve_k)
        context = self._rerank_context(raw_context, top_n=max(3, min(5, top_k)))
        payload = build_prompt_payload(inp=inp, dom_snippet=dom_snippet, context_candidates=context)
        rules = payload.setdefault("rules", {})
        rules["prefer_compact_dsl"] = True
        rules["max_candidates"] = max(1, min(5, top_k))
        raw = await self.llm.suggest_locators(payload)
        suggestions = self._parse_suggestions(raw)
        if top_k > 0:
            return suggestions[:top_k]
        return suggestions

    @staticmethod
    def _build_query(inp: BuildInput, dom_snippet: str) -> str:
        return (
            f"page={inp.page_name}; element={inp.element_name}; field_type={inp.field_type}; "
            f"vars={inp.vars}; dom={dom_snippet[:2000]}"
        )

    @staticmethod
    def _rerank_context(context: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
        scored: list[tuple[float, int, dict[str, Any]]] = []
        for idx, item in enumerate(context):
            if not isinstance(item, dict):
                continue
            vector_similarity = float(item.get("similarity") or item.get("vector_similarity") or item.get("score") or 0.0)
            structural_similarity = float(item.get("structural_similarity") or 0.0)
            quality = item.get("quality_metrics") if isinstance(item.get("quality_metrics"), dict) else {}
            stability = float(item.get("stability_score") or quality.get("stability_score") or 0.0)
            uniqueness = float(item.get("uniqueness_score") or quality.get("uniqueness_score") or 0.0)
            rerank = (
                0.45 * vector_similarity
                + 0.25 * structural_similarity
                + 0.20 * stability
                + 0.10 * uniqueness
            )
            enriched = dict(item)
            enriched["rerank_score"] = round(rerank, 6)
            scored.append((rerank, -idx, enriched))

        scored.sort(reverse=True)
        return [entry for _, _, entry in scored[: max(1, top_n)]]

    @staticmethod
    def _parse_suggestions(raw: list[dict[str, Any]]) -> list[LocatorSpec]:
        out: list[LocatorSpec] = []
        seen: set[str] = set()
        for item in raw:
            try:
                candidate = LocatorSpec(
                    kind=str(item["kind"]),
                    value=str(item["value"]),
                    options=dict(item.get("options") or {}),
                    scope=LocatorSpec.from_dict(item["scope"]) if item.get("scope") else None,
                )
                if RagAssist._is_weak_locator(candidate):
                    continue
                stable = candidate.stable_hash()
                if stable in seen:
                    continue
                seen.add(stable)
                out.append(candidate)
            except Exception:
                continue
        return out

    @staticmethod
    def _is_weak_locator(locator: LocatorSpec) -> bool:
        value = (locator.value or "").strip().casefold()
        if locator.kind == "css":
            return value in {"*", "html", "body", "div", "span"}
        if locator.kind == "xpath":
            return value in {"//*", "//html", "/html[1]"}
        return False
