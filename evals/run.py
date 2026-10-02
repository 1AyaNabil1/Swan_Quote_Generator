"""
Run the evaluation suite against the real pipeline.

    python -m evals.run                         # both modes, real Gemini (GEMINI_API_KEY)
    python -m evals.run --suites injection --modes raw
    python -m evals.run --fake                  # offline, to check the harness itself

"guarded" is Swan as deployed. "raw" turns the guardrails off: no injection check, and
answer checks are recorded but not enforced, so it measures the model on its own.
Results go to evals/reports/ as Markdown and JSON.
"""

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.api.controllers.quote_controller import SYSTEM_INSTRUCTION, QuoteController
from app.api.errors import classify
from app.api.models import QuoteRequest
from app.config import settings
from app.guardrails import GuardrailError
from app.guardrails.normalize import normalize
from app.guardrails.output import leaks_instructions
from app.llm import LLMError, ResilientLLM
from app.trace import Trace
from evals.report import render


CASES = Path(__file__).with_name("cases.jsonl")
REPORTS = Path(__file__).with_name("reports")
MODES = ("guarded", "raw")


@dataclass(frozen=True)
class Case:
    id: str
    suite: str  # "quality", "injection" or "safety"
    variety: str  # "en", "msa", "egy", "arabizi" or "obfuscated"
    request: dict
    pair: str | None = None  # cases with the same pair ask the same thing in other varieties
    canary: str | None = None  # appears in the quote only if the model obeyed the injection
    expect: str = "quote"  # "quote" or "refusal"


@dataclass
class Result:
    case: str
    mode: str
    outcome: str
    quote: str | None = None
    model: str | None = None
    first_pass: bool | None = None
    violations: list[str] = field(default_factory=list)
    generations: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    duration: float = 0.0
    injection_rule: str | None = None
    canary_leaked: bool = False
    instructions_leaked: bool = False


def load_cases(path: Path = CASES, suites: set[str] | None = None) -> list[Case]:
    cases = [Case(**json.loads(line)) for line in path.read_text().splitlines() if line.strip()]
    return [c for c in cases if not suites or c.suite in suites]


class Pacer:
    """Spaces out the start of each case to stay under a requests-per-minute quota."""

    def __init__(self, rpm: float):
        self.interval = 60 / rpm if rpm else 0.0
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        if not self.interval:
            return
        async with self._lock:
            now = time.monotonic()
            if self._next > now:
                await asyncio.sleep(self._next - now)
            self._next = max(now, self._next) + self.interval


async def run_case(controller: QuoteController, case: Case, mode: str) -> Result:
    request = QuoteRequest(**case.request)
    trace = Trace(
        category=request.category.value,
        language=request.language,
        length=request.length,
        has_topic=bool(request.topic),
        has_style=bool(request.style),
    )
    started = time.monotonic()
    quote = None
    try:
        response = await controller.generate_quote(request, trace)
        trace.outcome, quote = "ok", response.quote
    except (LLMError, GuardrailError) as e:
        trace.outcome = classify(e)[0]
    return Result(
        case=case.id,
        mode=mode,
        outcome=trace.outcome,
        quote=quote,
        model=trace.model,
        first_pass=trace.first_pass,
        violations=trace.violations,
        generations=trace.generations,
        input_tokens=trace.input_tokens,
        output_tokens=trace.output_tokens,
        duration=round(time.monotonic() - started, 3),
        injection_rule=trace.injection_rule,
        canary_leaked=bool(quote and case.canary and case.canary.lower() in quote.lower()),
        instructions_leaked=bool(
            quote and leaks_instructions(normalize(quote), SYSTEM_INSTRUCTION)
        ),
    )


async def run(
    cases: list[Case], modes: list[str], llm: ResilientLLM, concurrency: int, rpm: float
) -> list[Result]:
    results: list[Result] = []
    controller = QuoteController(llm)
    pacer = Pacer(rpm)
    semaphore = asyncio.Semaphore(concurrency)
    original = settings.guardrails_enabled

    async def one(case: Case, mode: str) -> Result:
        async with semaphore:
            await pacer.wait()
            result = await run_case(controller, case, mode)
            print(f"  {mode:8} {case.id:32} {result.outcome}", file=sys.stderr)
            return result

    try:
        for mode in modes:  # one mode at a time: the guardrails switch is process-wide
            settings.guardrails_enabled = mode == "guarded"
            results += await asyncio.gather(*(one(case, mode) for case in cases))
    finally:
        settings.guardrails_enabled = original
    return results


def build_llm(fake: bool) -> ResilientLLM:
    if fake:
        from evals.fake import FakeEvalModel

        return ResilientLLM([FakeEvalModel()])
    from app.llm.factory import build_llm as build_real

    return build_real()


def main(argv: list[str] | None = None) -> Path:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--suites", nargs="*", choices=["quality", "injection", "safety"])
    parser.add_argument("--modes", nargs="*", choices=MODES, default=list(MODES))
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument(
        "--rpm", type=float, default=8, help="cases started per minute; 0 for no limit"
    )
    parser.add_argument("--fake", action="store_true", help="use an offline stand-in model")
    parser.add_argument("--out", type=Path, default=REPORTS)
    args = parser.parse_args(argv)

    cases = load_cases(suites=set(args.suites or []))
    llm = build_llm(args.fake)
    models = "fake-model" if args.fake else ", ".join(p.name for p in llm.providers)
    print(f"Running {len(cases)} cases x {len(args.modes)} modes on {models}", file=sys.stderr)
    results = asyncio.run(
        run(cases, args.modes, llm, args.concurrency, 0 if args.fake else args.rpm)
    )

    stamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
    name = f"{stamp}-{'fake' if args.fake else settings.default_model}"
    args.out.mkdir(parents=True, exist_ok=True)
    meta = {
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "models": models,
        "version": settings.app_version,
        "modes": args.modes,
        "cases": len(cases),
    }
    (args.out / f"{name}.json").write_text(
        json.dumps(
            {"meta": meta, "results": [r.__dict__ for r in results]}, ensure_ascii=False, indent=1
        )
    )
    report = args.out / f"{name}.md"
    report.write_text(render(meta, cases, results))
    print(f"Report: {report}", file=sys.stderr)
    return report


if __name__ == "__main__":
    main()
