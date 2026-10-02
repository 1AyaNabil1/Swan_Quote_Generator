"""
A record of one quote generation: what was asked, each model call, each failed check,
and how it ended. Logged as one line per request.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any

from app import observability as metrics
from app.llm import Attempt, LLMResult


logger = logging.getLogger("swan.generation")


@dataclass
class Trace:
    category: str
    language: str
    length: str
    request_id: str = field(default_factory=metrics.request_id_var.get)
    has_topic: bool = False
    has_style: bool = False
    outcome: str = "unknown"
    model: str | None = None  # the model whose answer was returned
    injection_rule: str | None = None
    attempts: list[Attempt] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)  # failed checks, across generations
    first_pass: bool | None = None  # whether the first answer passed every check
    generations: int = 0  # answers received, including ones the checks rejected
    input_tokens: int = 0
    output_tokens: int = 0
    duration: float = 0.0

    def record(self, result: LLMResult) -> None:
        self.generations += 1
        self.input_tokens += result.input_tokens
        self.output_tokens += result.output_tokens

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["attempts"] = [{**a, "latency": round(a["latency"], 3)} for a in data["attempts"]]
        data["duration"] = round(self.duration, 3)
        return data


def observe(trace: Trace) -> None:
    """Log the finished generation and count it. Topic and style are not logged, only
    whether they were given: they are user text."""
    logger.info(json.dumps(trace.to_dict(), ensure_ascii=False))

    metrics.GENERATIONS.labels(trace.outcome, trace.language).inc()
    for attempt in trace.attempts:
        metrics.MODEL_CALLS.labels(attempt.model, attempt.outcome).inc()
        if attempt.outcome != "CircuitOpen":
            metrics.MODEL_DURATION.labels(attempt.model).observe(attempt.latency)
    metrics.TOKENS.labels("input").inc(trace.input_tokens)
    metrics.TOKENS.labels("output").inc(trace.output_tokens)
    for check in trace.violations:
        metrics.VIOLATIONS.labels(check).inc()
    if trace.generations > 1:
        metrics.REGENERATIONS.inc(trace.generations - 1)
    if trace.injection_rule:
        metrics.INJECTIONS.labels(trace.injection_rule).inc()
