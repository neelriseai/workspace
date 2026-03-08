"""OpenAI embedder adapter."""

from __future__ import annotations

from xpath_healer.rag.embedder import Embedder

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - optional dependency
    AsyncOpenAI = None  # type: ignore[assignment]


class OpenAIEmbedder(Embedder):
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int | None = None,
    ) -> None:
        if AsyncOpenAI is None:
            raise RuntimeError("openai is not installed. Install with: python -m pip install openai")
        self.api_key = (api_key or "").strip()
        self.model = model
        self.dimensions = int(dimensions) if dimensions is not None else None
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIEmbedder.")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def embed_text(self, text: str) -> list[float]:
        kwargs = {"model": self.model, "input": text}
        if self.dimensions is not None and self.dimensions > 0:
            kwargs["dimensions"] = self.dimensions
        try:
            response = await self.client.embeddings.create(**kwargs)
        except Exception:
            if "dimensions" not in kwargs:
                raise
            response = await self.client.embeddings.create(model=self.model, input=text)
        data = response.data[0].embedding if response.data else []
        return [float(value) for value in data]
