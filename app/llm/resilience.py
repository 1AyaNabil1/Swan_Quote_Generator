"""
Retries, a fallback chain of models, and a circuit breaker per model.
"""

import asyncio
import logging
import random
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from app.llm.base import (
    CircuitOpen,
    LLMError,
    LLMProvider,
    LLMRequest,
    LLMResult,
    Refused,
    TimedOut,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Attempt:
    """One call to one model, for the request's trace."""

    model: str
    outcome: str  # "ok", or the error class name, e.g. "RateLimited"
    latency: float = 0.0


class CircuitBreaker:
    """Stops calling a model after `threshold` failures in a row, for `cooldown` seconds.

    After the cooldown, calls go through again (half-open); one more failure opens the
    circuit again straight away, one success closes it.
    """

    def __init__(
        self, threshold: int, cooldown: float, clock: Callable[[], float] = time.monotonic
    ):
        self.threshold = threshold
        self.cooldown = cooldown
        self._clock = clock
        self.failures = 0
        self.opened_at: float | None = None

    @property
    def state(self) -> str:
        if self.opened_at is None:
            return "closed"
        return "half_open" if self._clock() - self.opened_at >= self.cooldown else "open"

    def allow(self) -> bool:
        return self.state != "open"

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = self._clock()


class ResilientLLM:
    """Tries each model in order until one answers.

    - An outage or dropped connection is retried on the same model, with backoff.
    - A rate limit, a timeout or a rejected request moves on to the next model.
    - A refusal ends the chain: asking another model would be a way around the
      safety filters.
    - Everything shares one deadline, so fallbacks can't stretch a request past it,
      and `attempt_timeout` caps each call so a hanging model leaves time for the next.
    """

    def __init__(
        self,
        providers: Sequence[LLMProvider],
        *,
        retries: int = 1,
        backoff: float = 0.25,
        attempt_timeout: float | None = None,
        breaker_threshold: int = 5,
        breaker_cooldown: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        if not providers:
            raise ValueError("ResilientLLM needs at least one provider")
        self.providers = list(providers)
        self.retries = retries
        self.backoff = backoff
        self.attempt_timeout = attempt_timeout
        self.breakers = {
            p.name: CircuitBreaker(breaker_threshold, breaker_cooldown, clock)
            for p in self.providers
        }
        self._clock = clock
        self._sleep = sleep

    async def generate(
        self, request: LLMRequest, deadline: float, attempts: list[Attempt]
    ) -> LLMResult:
        """Return the first model's answer. Each call is appended to `attempts`.
        `deadline` is a time on the `clock` this instance was built with."""
        error: LLMError = TimedOut("deadline passed before any model was called")
        for provider in self.providers:
            breaker = self.breakers[provider.name]
            if not breaker.allow():
                attempts.append(Attempt(provider.name, "CircuitOpen"))
                error = CircuitOpen(f"{provider.name}: circuit open")
                continue

            for retry in range(self.retries + 1):
                remaining = deadline - self._clock()
                if remaining <= 0:
                    raise error
                started = self._clock()
                try:
                    timeout = min(remaining, self.attempt_timeout or remaining)
                    result = await provider.generate(request, timeout=timeout)
                except Refused:
                    breaker.record_success()  # the model is working; it said no
                    attempts.append(Attempt(provider.name, "Refused", self._clock() - started))
                    raise
                except LLMError as e:
                    breaker.record_failure()
                    attempts.append(
                        Attempt(provider.name, type(e).__name__, self._clock() - started)
                    )
                    logger.warning(f"Model call failed: {e}")
                    error = e
                    if e.retryable and retry < self.retries:
                        delay = self.backoff * 2**retry * random.uniform(0.5, 1.0)
                        await self._sleep(min(delay, max(0.0, deadline - self._clock())))
                        continue
                    break
                else:
                    breaker.record_success()
                    attempts.append(Attempt(provider.name, "ok", result.latency))
                    return result

            if not error.fallback:
                raise error
        raise error
