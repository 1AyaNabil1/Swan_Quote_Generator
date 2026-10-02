"""
In-memory rate limiting for the quote endpoints.

Every quote is a paid Gemini call, so requests are limited per client and in total.
The counters live in the process: with several uvicorn workers each has its own, and a
restart clears them. That is enough to stop one visitor or script from draining the
quota; it is not a substitute for limits at the edge.
"""

import math
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request, Response

from app.config import settings
from app.observability import RATE_LIMITED


class SlidingWindowLimiter:
    """Allows at most `limit` hits per key in any `window` seconds."""

    def __init__(
        self, limit: int, window: float = 60.0, clock: Callable[[], float] = time.monotonic
    ):
        self.limit = limit
        self.window = window
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._calls = 0

    def hit(self, key: str) -> float | None:
        """Record a hit for `key`. Returns None if allowed, else seconds until one is."""
        now = self._clock()
        hits = self._hits.setdefault(key, deque())
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return self.window - (now - hits[0])
        hits.append(now)
        self._calls += 1
        if self._calls % 1000 == 0:
            self._sweep(now)
        return None

    def remaining(self, key: str) -> int:
        """Hits `key` has left in the current window, as of its last hit."""
        return max(0, self.limit - len(self._hits.get(key, ())))

    def _sweep(self, now: float) -> None:
        """Forget keys with no hits inside the window, so memory stays bounded."""
        for key in [k for k, h in self._hits.items() if not h or now - h[-1] >= self.window]:
            del self._hits[key]

    def reset(self) -> None:
        self._hits.clear()
        self._calls = 0


per_client = SlidingWindowLimiter(settings.rate_limit_per_client)
overall = SlidingWindowLimiter(settings.rate_limit_global)


def client_key(request: Request) -> str:
    """The client's address. Cloudflare sets CF-Connecting-IP and Render's proxy sets
    X-Forwarded-For; both can be forged by a client that bypasses them, which is why
    the global limit exists."""
    ip = request.headers.get("cf-connecting-ip", "").strip()
    if not ip:
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not ip and request.client:
        ip = request.client.host
    return ip or "unknown"


async def enforce_rate_limit(request: Request, response: Response) -> None:
    """FastAPI dependency: raise 429 when the client or the whole app is over its limit.
    Allowed responses say how many quotes the client has left, so the UI can warn."""
    if not settings.rate_limit_enabled:
        return
    key = client_key(request)
    for scope, limiter, limiter_key in (("client", per_client, key), ("global", overall, "all")):
        wait = limiter.hit(limiter_key)
        if wait is not None:
            RATE_LIMITED.labels(scope).inc()
            seconds = max(1, math.ceil(wait))
            raise HTTPException(
                429,
                f"Too many quotes at once. Try again in {seconds} seconds.",
                headers={"Retry-After": str(seconds)},
            )
    response.headers["X-RateLimit-Limit"] = str(per_client.limit)
    response.headers["X-RateLimit-Remaining"] = str(per_client.remaining(key))
