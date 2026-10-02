"""
Unit tests for the rate limiter and the quote cleaning.
"""

from app.api.utils.ai_client import AIClient
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


def test_limiter_forgets_idle_clients():
    clock = Clock()
    limiter = SlidingWindowLimiter(5, window=60, clock=clock)
    limiter.hit("idle")
    clock.now += 120
    for n in range(1000):
        limiter.hit(f"client-{n % 500}")
    assert "idle" not in limiter._hits


def clean(text):
    return AIClient.__new__(AIClient)._clean_quote_response(text)


def test_clean_removes_meta_prefixes():
    assert clean("Here is your quote: Stay curious.") == "Stay curious."
    assert clean("As an AI, Patience is a quiet strength.") == "Patience is a quiet strength."


def test_clean_drops_an_english_translation():
    arabic = "الصبر مفتاح الفرج"
    assert clean(f"**Arabic:** {arabic}\n\n**English Translation:** Patience is the key") == arabic


def test_clean_strips_markdown_emphasis():
    assert clean("**Be bold.**") == "Be bold."
