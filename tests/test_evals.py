"""
The eval harness, run offline with a model that has no defenses of its own.
"""

from evals.run import load_cases, main


def test_cases_are_valid_requests():
    from app.api.models import QuoteRequest

    cases = load_cases()
    assert len({c.id for c in cases}) == len(cases)
    for case in cases:
        QuoteRequest(**case.request)
        assert case.suite in {"quality", "injection", "safety"}
        assert case.expect in {"quote", "refusal"}


def test_offline_run_writes_a_report(tmp_path):
    report = main(["--fake", "--out", str(tmp_path)])
    text = report.read_text()
    assert report.with_suffix(".json").exists()
    for heading in ("## Quality", "## Prompt injection", "## Safety and parity", "## Every answer"):
        assert heading in text


def test_guardrails_stop_what_an_undefended_model_obeys(tmp_path):
    import json

    report = main(["--fake", "--suites", "injection", "--out", str(tmp_path)])
    results = json.loads(report.with_suffix(".json").read_text())["results"]
    leaked = {
        mode: sum(r["canary_leaked"] for r in results if r["mode"] == mode)
        for mode in ("guarded", "raw")
    }
    canaries = sum(1 for c in load_cases(suites={"injection"}) if c.canary)
    assert leaked == {"guarded": 0, "raw": canaries}
