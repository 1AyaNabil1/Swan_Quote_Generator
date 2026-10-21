"""
Writes static/src/lib/parity.fixture.json: what the Python guardrails say about every
string in tests/test_guardrails.py and evals/cases.jsonl. The browser port
(static/src/lib/*.js) is tested against it, so both keep saying the same thing.

    python scripts/guardrail_parity.py
"""

import ast
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.controllers.quote_controller import SYSTEM_INSTRUCTION
from app.guardrails import check_quote, clean_quote, scan_text
from app.guardrails.normalize import normalize, squash


ROOT = Path(__file__).resolve().parent.parent


def strings() -> list[str]:
    found: list[str] = []
    tree = ast.parse((ROOT / "tests" / "test_guardrails.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.strip():
            found.append(node.value)
    for line in (ROOT / "evals" / "cases.jsonl").read_text(encoding="utf-8").splitlines():
        request = json.loads(line)["request"]
        found += [request[key] for key in ("topic", "style") if request.get(key)]
    return list(dict.fromkeys(found))


def main() -> None:
    cases = []
    for text in strings():
        finding = scan_text("topic", text)
        cases.append(
            {
                "text": text,
                "normalize": normalize(text),
                "squash": squash(text),
                "clean": clean_quote(text),
                "scan": finding.rule if finding else None,
                "check": {
                    f"{language}-{finish}": [
                        [v.check, v.hint]
                        for v in check_quote(
                            text,
                            language=language,
                            length="medium",
                            finish_reason=finish,
                            instructions=SYSTEM_INSTRUCTION,
                        )
                    ]
                    for language in ("en", "ar")
                    for finish in ("stop", "max_tokens")
                },
            }
        )
    out = ROOT / "static" / "src" / "lib" / "parity.fixture.json"
    out.write_text(
        json.dumps(
            {"instructions": SYSTEM_INSTRUCTION, "cases": cases}, ensure_ascii=False, indent=1
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{len(cases)} strings -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
