"""Prompt payload builder utilities for RAG stage."""

from __future__ import annotations

import re
from typing import Any

from xpath_healer.core.models import BuildInput
from xpath_healer.rag.prompt_dsl import build_prompt_dsl


def build_prompt_payload(
    inp: BuildInput,
    dom_snippet: str,
    context_candidates: list[dict[str, Any]],
    deep_graph: bool = False,
) -> dict[str, Any]:
    dom_signature = build_dom_signature(dom_snippet, deep_graph=deep_graph)
    compact_context = _compact_context_candidates(context_candidates)
    return {
        "task": "suggest_locator_specs",
        "mode": "deep_graph" if deep_graph else "default",
        "field_type": inp.field_type,
        "dom_signature": dom_signature,
        "dsl_prompt": build_prompt_dsl(inp, dom_signature, compact_context, deep_graph=deep_graph),
        "context": compact_context,
        "rules": {
            "no_absolute_xpath_with_deep_indices": True,
            "avoid_positional_xpath": True,
            "prefer_css_or_role_when_unique": True,
            "bound_to_candidate_universe": True,
            "max_candidates": 5,
            "output_schema": {
                "kind": "css|xpath|role|text|pw",
                "value": "string",
                "options": "object",
                "confidence": "number [0..1], optional",
                "reason": "string, optional",
                "needs_more_context": "boolean, optional",
            },
        },
    }


def build_dom_signature(dom_snippet: str, deep_graph: bool = False) -> str:
    snippet_limit = 12000 if deep_graph else 5000
    snippet = (dom_snippet or "")[:snippet_limit]
    if not snippet:
        return ""
    tags = ("input", "button", "a", "select", "textarea", "label")
    counts = []
    for tag in tags:
        count = len(re.findall(fr"<\s*{tag}\b", snippet, flags=re.IGNORECASE))
        if count > 0:
            counts.append(f"{tag}:{count}")

    role_hits = re.findall(r'role\s*=\s*["\']([^"\']+)["\']', snippet, flags=re.IGNORECASE)
    testid_hits = re.findall(r'data-testid\s*=\s*["\']([^"\']+)["\']', snippet, flags=re.IGNORECASE)
    placeholder_hits = re.findall(r'placeholder\s*=\s*["\']([^"\']+)["\']', snippet, flags=re.IGNORECASE)
    labels = re.findall(r"<label[^>]*>(.*?)</label>", snippet, flags=re.IGNORECASE | re.DOTALL)

    token_limit = 8 if deep_graph else 4
    roles = _top_tokens(role_hits, limit=token_limit)
    testids = _top_tokens(testid_hits, limit=token_limit)
    placeholders = _top_tokens(placeholder_hits, limit=token_limit)
    label_tokens = _top_tokens([" ".join(item.split())[:40] for item in labels], limit=5 if deep_graph else 3)

    parts = [f"tags[{', '.join(counts)}]"] if counts else []
    if roles:
        parts.append(f"roles[{', '.join(roles)}]")
    if testids:
        parts.append(f"testids[{', '.join(testids)}]")
    if placeholders:
        parts.append(f"placeholders[{', '.join(placeholders)}]")
    if label_tokens:
        parts.append(f"labels[{', '.join(label_tokens)}]")

    compact_limit = 380 if deep_graph else 180
    compact = " ".join(snippet.split())
    compact = compact[:compact_limit] + ("..." if len(compact) > compact_limit else "")
    if compact:
        parts.append(f"sample={compact}")
    return " ".join(parts)


def _top_tokens(values: list[str], limit: int = 4) -> list[str]:
    uniq: list[str] = []
    seen: set[str] = set()
    for raw in values:
        token = " ".join((raw or "").split()).strip()
        if not token:
            continue
        key = token.casefold()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(token[:40])
        if len(uniq) >= limit:
            break
    return uniq


def _compact_context_candidates(context_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked = context_candidates[:5]
    common_scope = _common_scope(picked)

    out: list[dict[str, Any]] = []
    for item in picked:
        if not isinstance(item, dict):
            continue
        compact: dict[str, Any] = {}
        for key in ("app_id", "page_name", "field_type"):
            value = item.get(key)
            if value is None:
                continue
            if common_scope.get(key) == value:
                continue
            compact[key] = value

        for key in ("element_name", "rerank_score"):
            value = item.get(key)
            if value is not None:
                compact[key] = value

        locator_payload = None
        for locator_key in ("locator", "last_good_locator", "robust_locator"):
            loc = item.get(locator_key)
            if isinstance(loc, dict) and loc.get("kind") and loc.get("value"):
                locator_payload = {"kind": loc.get("kind"), "value": loc.get("value")}
                break
        if locator_payload:
            compact["locator"] = locator_payload

        quality = item.get("quality_metrics")
        if isinstance(quality, dict):
            compact["quality"] = {
                "stability": quality.get("stability_score"),
                "uniqueness": quality.get("uniqueness_score"),
            }
        metadata = item.get("metadata")
        if isinstance(metadata, dict):
            if metadata.get("prompt_compact_text"):
                compact["prompt_compact_text"] = str(metadata.get("prompt_compact_text"))[:240]
            if metadata.get("fingerprint_tokens"):
                compact["fingerprint_tokens"] = list(metadata.get("fingerprint_tokens") or [])[:6]
        out.append(compact)
    return out


def _common_scope(items: list[dict[str, Any]]) -> dict[str, Any]:
    keys = ("app_id", "page_name", "field_type")
    out: dict[str, Any] = {}
    if not items:
        return out
    for key in keys:
        value = None
        same = True
        for item in items:
            if not isinstance(item, dict):
                same = False
                break
            current = item.get(key)
            if value is None:
                value = current
            elif current != value:
                same = False
                break
        if same and value not in (None, ""):
            out[key] = value
    return out
