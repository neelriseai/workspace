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
            "Return only JSON with a top-level key `candidates` that is an array of locator objects."
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
            candidates = payload.get("candidates")
            if isinstance(candidates, list):
                return [item for item in candidates if isinstance(item, dict)]
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
