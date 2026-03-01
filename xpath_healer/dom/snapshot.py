"""Playwright DOM snapshotter with small TTL cache."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SnapshotRecord:
    html: str
    captured_at: float


class DomSnapshotter:
    def __init__(self, cache_ttl_sec: int = 30) -> None:
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: dict[int, SnapshotRecord] = {}

    async def capture(self, page: Any, scoped_locator: Any | None = None, use_cache: bool = True) -> str:
        cache_key = id(scoped_locator or page)
        now = time.time()
        cached = self._cache.get(cache_key)
        if use_cache and cached and (now - cached.captured_at) <= self.cache_ttl_sec:
            return cached.html

        if scoped_locator is not None:
            html = await scoped_locator.evaluate("el => el.outerHTML")
        else:
            html = await page.evaluate("() => document.documentElement ? document.documentElement.outerHTML : ''")

        html = html or ""
        self._cache[cache_key] = SnapshotRecord(html=html, captured_at=now)
        return html

