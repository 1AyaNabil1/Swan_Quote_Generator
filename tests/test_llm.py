"""
The resilience layer with fake models and a fake clock: retries, fallbacks, the
deadline and the circuit breaker.
"""

import pytest

from app.llm import (
    BadRequest,
    CircuitBreaker,
    CircuitOpen,
    LLMRequest,
    LLMResult,
    RateLimited,
    Refused,
    ResilientLLM,
    TimedOut,
    Unavailable,
)
from app.llm.gemini import ModelSpec


REQUEST = LLMRequest(prompt="p", system="s", max_tokens=100, temperature=0.5)


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class FakeProvider:
    """Answers with the next item of `answers`: an LLMError to raise, or text."""

    def __init__(self, name, *answers, clock=None, takes=0.0):
        self.name = name
        self.answers = list(answers)
        self.timeouts = []
        self.clock = clock
        self.takes = takes

    async def generate(self, request, timeout):
        self.timeouts.append(timeout)
        if self.clock:
            self.clock.now += self.takes
        answer = self.answers.pop(0) if self.answers else "ok"
        if isinstance(answer, Exception):
            raise answer
        return LLMResult(text=answer, model=self.name, finish_reason="stop")


async def no_sleep(_):
    pass


def chain(*providers, clock=None, **kwargs):
    return ResilientLLM(providers, clock=clock or Clock(), sleep=no_sleep, **kwargs)


async def run(llm, deadline=1e9):
    attempts = []
    try:
        return await llm.generate(REQUEST, deadline, attempts), attempts
    except Exception as e:
        e.attempts = attempts
        raise


async def test_first_model_answers():
    result, attempts = await run(chain(FakeProvider("a", "hello"), FakeProvider("b")))
    assert result.text == "hello"
    assert [(a.model, a.outcome) for a in attempts] == [("a", "ok")]


async def test_outage_is_retried_then_falls_back():
    a = FakeProvider("a", Unavailable("down"), Unavailable("still down"))
    result, attempts = await run(chain(a, FakeProvider("b", "from b"), retries=1))
    assert result.model == "b"
    assert [a.outcome for a in attempts] == ["Unavailable", "Unavailable", "ok"]


async def test_rate_limit_falls_back_without_retrying():
    result, attempts = await run(chain(FakeProvider("a", RateLimited("429")), FakeProvider("b")))
    assert result.model == "b"
    assert [a.model for a in attempts] == ["a", "b"]


async def test_refusal_stops_the_chain():
    b = FakeProvider("b")
    with pytest.raises(Refused):
        await run(chain(FakeProvider("a", Refused("no")), b))
    assert b.timeouts == []


async def test_bad_request_on_every_model_raises_the_last_error():
    with pytest.raises(BadRequest):
        await run(chain(FakeProvider("a", BadRequest("404")), FakeProvider("b", BadRequest("400"))))


async def test_deadline_is_shared_and_each_call_is_capped():
    clock = Clock()
    a = FakeProvider("a", TimedOut("slow"), clock=clock, takes=4)
    b = FakeProvider("b", clock=clock, takes=1)
    await run(chain(a, b, clock=clock, attempt_timeout=4), deadline=clock.now + 10)
    assert a.timeouts == [4]  # capped, so b still had time
    assert b.timeouts == [4]


async def test_passed_deadline_stops_before_the_next_model():
    clock = Clock()
    a = FakeProvider("a", TimedOut("slow"), clock=clock, takes=10)
    b = FakeProvider("b")
    with pytest.raises(TimedOut):
        await run(chain(a, b, clock=clock), deadline=clock.now + 10)
    assert b.timeouts == []


async def test_open_circuit_skips_the_model_until_the_cooldown_ends():
    clock = Clock()
    a = FakeProvider("a", *[RateLimited("429")] * 2)
    llm = chain(a, FakeProvider("b"), clock=clock, breaker_threshold=2, breaker_cooldown=30)
    await run(llm)
    await run(llm)  # second failure in a row opens a's circuit
    assert llm.breakers["a"].state == "open"

    _, attempts = await run(llm)
    assert [(x.model, x.outcome) for x in attempts] == [("a", "CircuitOpen"), ("b", "ok")]

    clock.now += 30
    assert llm.breakers["a"].state == "half_open"
    _, attempts = await run(llm)  # a has recovered
    assert [(x.model, x.outcome) for x in attempts] == [("a", "ok")]
    assert llm.breakers["a"].state == "closed"


async def test_all_circuits_open_is_reported_as_such():
    llm = chain(FakeProvider("a", RateLimited("429")), breaker_threshold=1)
    with pytest.raises(RateLimited):
        await run(llm)
    with pytest.raises(CircuitOpen):
        await run(llm)


def test_breaker_reopens_after_a_failed_trial():
    clock = Clock()
    breaker = CircuitBreaker(threshold=2, cooldown=10, clock=clock)
    breaker.record_failure()
    assert breaker.allow()
    breaker.record_failure()
    assert not breaker.allow()
    clock.now += 10
    assert breaker.allow()
    breaker.record_failure()
    assert not breaker.allow()
    breaker.record_success()
    assert breaker.state == "closed"


def test_resilient_llm_needs_a_model():
    with pytest.raises(ValueError):
        ResilientLLM([])


@pytest.mark.parametrize(
    ("text", "spec"),
    [
        ("gemini-2.5-flash", ModelSpec("gemini-2.5-flash")),
        ("gemini-2.5-flash@0", ModelSpec("gemini-2.5-flash", thinking_budget=0)),
        ("gemini-2.5-flash@none", ModelSpec("gemini-2.5-flash")),
        (
            "gemini-3.5-flash-lite@minimal",
            ModelSpec("gemini-3.5-flash-lite", thinking_level="MINIMAL"),
        ),
        (" gemini-3.8-flash@LOW ", ModelSpec("gemini-3.8-flash", thinking_level="LOW")),
    ],
)
def test_model_spec_parse(text, spec):
    assert ModelSpec.parse(text) == spec


@pytest.mark.parametrize("text", ["", "@0", "gemini@lots"])
def test_model_spec_parse_rejects_nonsense(text):
    with pytest.raises(ValueError):
        ModelSpec.parse(text)


@pytest.mark.parametrize(
    ("default_model", "budget", "spec"),
    [
        ("gemini-2.5-flash", 0, ModelSpec("gemini-2.5-flash", thinking_budget=0)),
        ("gemini-2.5-flash", None, ModelSpec("gemini-2.5-flash")),
        ("gemini-2.5-flash@512", 0, ModelSpec("gemini-2.5-flash", thinking_budget=512)),
        # THINKING_BUDGET is not applied to 3.x models, which reject or ignore it
        ("gemini-3.5-flash-lite", 0, ModelSpec("gemini-3.5-flash-lite")),
        (
            "gemini-3.5-flash-lite@minimal",
            0,
            ModelSpec("gemini-3.5-flash-lite", thinking_level="MINIMAL"),
        ),
    ],
)
def test_primary_spec(monkeypatch, default_model, budget, spec):
    from app.config import settings
    from app.llm.factory import primary_spec

    monkeypatch.setattr(settings, "default_model", default_model)
    monkeypatch.setattr(settings, "thinking_budget", budget)
    assert primary_spec() == spec


def test_model_spec_round_trips_as_text():
    for text in ("gemini-2.5-flash", "gemini-2.5-flash@0", "gemini-3.5-flash-lite@minimal"):
        assert str(ModelSpec.parse(text)) == text
