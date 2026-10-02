"""
A record of one quote generation: what was asked, each model call, each failed check,
and how it ended. Logged as one line per request.
"""

import json
import logging
from dataclasses import asdict, dataclass, field

from app.llm import Attempt, LLMResult


logger = logging.getLogger("swan.generation")


@dataclass
class Trace:
    category: str
    language: str
    length: str
    has_topic: bool = False
    has_style: bool = False
    outcome: str = "unknown"
    model: str | None = None  # the model whose answer was returned
    injection_rule: str | None = None
    attempts: list[Attempt] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)  # failed checks, across generations
    generations: int = 0  # answers received, including ones the checks rejected
    input_tokens: int = 0
    output_tokens: int = 0
    duration: float = 0.0

    def record(self, result: LLMResult) -> None:
        self.generations += 1
        self.input_tokens += result.input_tokens
        self.output_tokens += result.output_tokens

    def to_dict(self) -> dict:
        data = asdict(self)
        data["attempts"] = [{**a, "latency": round(a["latency"], 3)} for a in data["attempts"]]
        data["duration"] = round(self.duration, 3)
        return data


def observe(trace: Trace) -> None:
    """Log the finished generation. Topic and style are not logged, only whether they
    were given: they are user text."""
    logger.info(json.dumps(trace.to_dict(), ensure_ascii=False))
