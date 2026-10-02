"""
Unit tests for the rate limiter.
"""

from app.api.utils.rate_limit import SlidingWindowLimiter


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_limiter_allows_up_to_the_limit_then_says_how_long_to_wait():
    clock = Clock()
    limiter = SlidingWindowLimiter(2, window=60, clock=clock)
    assert limiter.hit("a") is None
    clock.now += 10
    assert limiter.hit("a") is None
    clock.now += 5
    assert limiter.hit("a") == 45  # the first hit leaves the window 45 s from now


def test_limiter_window_slides():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, window=60, clock=clock)
    assert limiter.hit("a") is None
    assert limiter.hit("a") is not None
    clock.now += 60
    assert limiter.hit("a") is None


def test_limiter_keys_are_independent():
    limiter = SlidingWindowLimiter(1, window=60, clock=Clock())
    assert limiter.hit("a") is None
    assert limiter.hit("b") is None
    assert limiter.hit("a") is not None


def test_limiter_counts_what_is_left():
    clock = Clock()
    limiter = SlidingWindowLimiter(2, window=60, clock=clock)
    assert limiter.remaining("a") == 2
    limiter.hit("a")
    assert limiter.remaining("a") == 1
    limiter.hit("a")
    limiter.hit("a")  # refused, so not counted
    assert limiter.remaining("a") == 0


def test_limiter_forgets_idle_clients():
    clock = Clock()
    limiter = SlidingWindowLimiter(5, window=60, clock=clock)
    limiter.hit("idle")
    clock.now += 120
    for n in range(1000):
        limiter.hit(f"client-{n % 500}")
    assert "idle" not in limiter._hits
