"""Compact prompt DSL builder for LLM fallback reasoning."""

from __future__ import annotations

from typing import Any

from xpath_healer.core.models import BuildInput
from xpath_healer.utils.text import normalize_text, safe_join


def build_prompt_dsl(
    inp: BuildInput,
    dom_snippet: str,
    context_candidates: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.extend(["ELEMENT", inp.element_name or "unknown", ""])

    lines.extend(["PAGE", inp.page_name or "unknown", ""])

    lines.extend(["SIGNATURE"])
    lines.append(f"field_type={inp.field_type}")
    if inp.intent.label:
        lines.append(f"label={inp.intent.label}")
    if inp.intent.text:
        lines.append(f"text={inp.intent.text}")
    if inp.intent.axis_hint:
        lines.append(f"axis_hint={inp.intent.axis_hint}")
    lines.append(f"occurrence={inp.intent.occurrence}")
    if inp.vars:
        compact_vars = safe_join([f"{k}={v}" for k, v in sorted(inp.vars.items())], sep="; ")
        lines.append(f"vars={compact_vars}")
    lines.append("")

    lines.extend(["FAILED_LOCATOR", _compact_locator(inp.fallback.to_dict()), ""])

    lines.append("CANDIDATES")
    for idx, item in enumerate(context_candidates, start=1):
        locator = _candidate_locator_line(item)
        score = item.get("rerank_score")
        if score is None:
            lines.append(f"{idx} {locator}")
        else:
            lines.append(f"{idx} {locator} score={float(score):.4f}")
    lines.append("")

    lines.extend(["DOM_SNIPPET", _compact_dom(dom_snippet, limit=1200), ""])
    lines.extend(
        [
            "INSTRUCTIONS",
            "Return JSON array only.",
            "Schema: [{\"kind\":\"css|xpath|role|text|pw\",\"value\":\"...\",\"options\":{...}}]",
            "Prefer stable attrs and short relative locators.",
            "Avoid absolute/deep-index xpaths.",
        ]
    )
    return "\n".join(lines).strip()


def _compact_dom(dom_snippet: str, limit: int = 1200) -> str:
    text = " ".join((dom_snippet or "").split())
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def _compact_locator(locator_payload: dict[str, Any]) -> str:
    kind = str(locator_payload.get("kind") or "")
    value = str(locator_payload.get("value") or "")
    return f"{kind}={value}"


def _candidate_locator_line(candidate: dict[str, Any]) -> str:
    for key in ("locator", "last_good_locator", "robust_locator"):
        value = candidate.get(key)
        if isinstance(value, dict) and value.get("kind") and value.get("value"):
            return _compact_locator(value)

    kind = candidate.get("kind")
    value = candidate.get("value")
    if kind and value:
        return f"{kind}={value}"

    page = normalize_text(str(candidate.get("page_name") or ""))
    element = normalize_text(str(candidate.get("element_name") or ""))
    return f"meta={page}.{element}".strip(".")
