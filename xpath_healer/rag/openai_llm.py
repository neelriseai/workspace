"""OpenAI LLM adapter for locator suggestion."""

from __future__ import annotations

import json
import re
from typing import Any

from xpath_healer.rag.llm import LLM

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - optional dependency
    AsyncOpenAI = None  # type: ignore[assignment]


_JSON_BLOCK_RE = re.compile(r"(\{.*\}|\[.*\])", flags=re.DOTALL)


class OpenAILLM(LLM):
    def __init__(self, api_key: str, model: str = "gpt-4.1") -> None:
        if AsyncOpenAI is None:
            raise RuntimeError("openai is not installed. Install with: python -m pip install openai")
        self.api_key = (api_key or "").strip()
        self.model = model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAILLM.")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def suggest_locators(self, prompt_payload: dict[str, Any]) -> list[dict[str, Any]]:
        system_prompt = (
            "You are a locator-repair assistant. "
            "Input contains compact symbol DSL + DOM signature + context. "
            "Use graph relations when present (G NODE/PARENT/LEFT/RIGHT/ANCHOR). "
            "Stay grounded in provided candidates/context and DOM facts; do not invent missing attributes. "
            "Return only JSON with top-level key `candidates` as an array of locator objects. "
            "Each candidate must include kind,value,options and should include confidence (0..1), reason, "
            "and may include needs_more_context=true when evidence is insufficient."
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=True)},
            ],
        )
        content = response.choices[0].message.content if response.choices else ""
        payload = self._parse_json_content(content)
        if isinstance(payload, dict):
            needs_more_context = bool(payload.get("needs_more_context"))
            candidates = payload.get("candidates")
            if isinstance(candidates, list):
                out: list[dict[str, Any]] = []
                for item in candidates:
                    if not isinstance(item, dict):
                        continue
                    enriched = dict(item)
                    if needs_more_context and "needs_more_context" not in enriched:
                        enriched["needs_more_context"] = True
                    out.append(enriched)
                return out
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    @staticmethod
    def _parse_json_content(content: str | None) -> Any:
        if not content:
            return None
        text = content.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        match = _JSON_BLOCK_RE.search(text)
        if not match:
            return None
        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            return None
