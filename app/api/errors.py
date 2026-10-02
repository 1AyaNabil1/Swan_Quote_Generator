"""
What each failure means for the user: an outcome name for logs and metrics, an HTTP
status, and a message that is safe to show. Details stay in the server log.
"""

from app.guardrails import GuardrailError, InputRejected
from app.llm import CircuitOpen, LLMError, RateLimited, Refused, TimedOut


BLOCKED_MESSAGE = "Swan can't write a quote about that. Try a different topic or style."
INJECTION_MESSAGE = (
    "Swan writes quotes about a topic; it doesn't follow instructions written in one. "
    "Try rephrasing the topic or style."
)
FAILED_MESSAGE = "Couldn't generate a quote this time. Please try again."
BUSY_MESSAGE = "Swan is busy right now. Please try again in a minute."
TIMEOUT_MESSAGE = "Quote generation timed out. Please try again."


def classify(error: LLMError | GuardrailError) -> tuple[str, int, str]:
    """(outcome, status, message) for a failed generation."""
    match error:
        case InputRejected():
            return "injection", 422, INJECTION_MESSAGE
        case Refused():
            return "refused", 422, BLOCKED_MESSAGE
        case RateLimited() | CircuitOpen():
            return "busy", 503, BUSY_MESSAGE
        case TimedOut():
            return "timeout", 504, TIMEOUT_MESSAGE
        case GuardrailError():
            return "rejected_output", 502, FAILED_MESSAGE
        case _:
            return "model_error", 502, FAILED_MESSAGE
