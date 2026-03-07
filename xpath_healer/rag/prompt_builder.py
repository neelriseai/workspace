"""Prompt payload builder utilities for RAG stage."""

from __future__ import annotations

from typing import Any

from xpath_healer.core.models import BuildInput
from xpath_healer.rag.prompt_dsl import build_prompt_dsl


def build_prompt_payload(
    inp: BuildInput,
    dom_snippet: str,
    context_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "task": "suggest_locator_specs",
        "field_type": inp.field_type,
        "intent": inp.intent.to_dict(),
        "vars": inp.vars,
        "dom_snippet": dom_snippet[:15000],
        "dsl_prompt": build_prompt_dsl(inp, dom_snippet, context_candidates),
        "context": context_candidates,
        "rules": {
            "no_absolute_xpath_with_deep_indices": True,
            "max_candidates": 5,
            "output_schema": {"kind": "css|xpath|role|text|pw", "value": "string", "options": "object"},
        },
    }
