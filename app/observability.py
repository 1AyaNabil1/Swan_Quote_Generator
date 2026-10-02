"""
Request IDs, log context and Prometheus metrics.

Metrics live in the process. The Docker image runs one uvicorn worker, so a scrape of
/metrics sees the whole service; with several workers each would report its own share.
"""

import contextvars
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable, Iterator, Mapping

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, disable_created_metrics
from prometheus_client.core import GaugeMetricFamily
from starlette.routing import Mount

from app.llm.resilience import CircuitBreaker


request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
# An incoming X-Request-ID is kept only if it is short and plain, so it is safe in logs
SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RequestIdFilter(logging.Filter):
    """Adds the current request's ID to every log record as `request_id`."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


disable_created_metrics()  # type: ignore[no-untyped-call]  # the *_created samples add nothing for a single process

HTTP_REQUESTS = Counter("swan_http_requests_total", "HTTP requests", ["method", "route", "status"])
HTTP_DURATION = Histogram(
    "swan_http_request_duration_seconds",
    "HTTP request duration",
    ["route"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30),
)
GENERATIONS = Counter(
    "swan_generations_total", "Quote requests by how they ended", ["outcome", "language"]
)
MODEL_CALLS = Counter("swan_model_calls_total", "Model calls by result", ["model", "outcome"])
MODEL_DURATION = Histogram(
    "swan_model_call_duration_seconds",
    "Model call duration",
    ["model"],
    buckets=(0.25, 0.5, 1, 2, 4, 8, 15, 30),
)
TOKENS = Counter("swan_model_tokens_total", "Tokens used, including rejected answers", ["kind"])
REGENERATIONS = Counter(
    "swan_regenerations_total", "Answers regenerated because they failed a check"
)
VIOLATIONS = Counter(
    "swan_output_check_failures_total", "Answers that failed an output check", ["check"]
)
INJECTIONS = Counter(
    "swan_injections_blocked_total", "Requests stopped by the injection check", ["rule"]
)
RATE_LIMITED = Counter("swan_rate_limited_total", "Requests refused by the rate limiter", ["scope"])
BUILD_INFO = Gauge(
    "swan_build_info", "Always 1; the labels say what is running", ["version", "model"]
)


class CircuitCollector:
    """Reports each model's circuit breaker at scrape time: 1 while open, else 0."""

    def __init__(self, breakers: Callable[[], Mapping[str, CircuitBreaker]]):
        self._breakers = breakers

    def collect(self) -> Iterator[GaugeMetricFamily]:
        gauge = GaugeMetricFamily(
            "swan_circuit_open", "1 while a model is skipped after failing", labels=["model"]
        )
        for model, breaker in self._breakers().items():
            gauge.add_metric([model], 1.0 if breaker.state == "open" else 0.0)
        yield gauge


def route_label(request: Request) -> str:
    """The route template, e.g. /api/quotes/generate, so paths can't explode the labels."""
    route = request.scope.get("route")
    if route is None:
        return "unmatched"
    if isinstance(route, Mount):
        return "static"
    return getattr(route, "path", "unmatched")


async def observe_http(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware: assign a request ID, time the request, count it."""
    incoming = request.headers.get("x-request-id", "")
    request_id = incoming if SAFE_REQUEST_ID.match(incoming) else uuid.uuid4().hex
    token = request_id_var.set(request_id)
    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        route = route_label(request)
        HTTP_REQUESTS.labels(request.method, route, str(status)).inc()
        HTTP_DURATION.labels(route).observe(time.perf_counter() - started)
        request_id_var.reset(token)
