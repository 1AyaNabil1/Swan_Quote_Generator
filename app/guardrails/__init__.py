"""
Guardrails: prompt-injection detection on the way in, checks on the answer on the way out.
"""

from app.guardrails.injection import Finding, scan_request, scan_text
from app.guardrails.output import Violation, check_quote, clean_quote


class GuardrailError(Exception):
    """A request or an answer that a guardrail stopped."""


class InputRejected(GuardrailError):
    def __init__(self, finding: Finding):
        super().__init__(f"{finding.field} matched {finding.rule}")
        self.finding = finding


class OutputRejected(GuardrailError):
    def __init__(self, violations: list[Violation]):
        super().__init__(", ".join(v.check for v in violations))
        self.violations = violations


__all__ = [
    "Finding",
    "GuardrailError",
    "InputRejected",
    "OutputRejected",
    "Violation",
    "check_quote",
    "clean_quote",
    "scan_request",
    "scan_text",
]
