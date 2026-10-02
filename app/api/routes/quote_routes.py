import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.controllers import QuoteController
from app.api.errors import classify
from app.api.models import ErrorResponse, QuoteCategory, QuoteRequest, QuoteResponse
from app.api.utils.rate_limit import enforce_rate_limit
from app.guardrails import GuardrailError
from app.llm import LLMError
from app.trace import Trace, observe


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

# Lazy initialization of controller
_controller = None


def circuit_breakers() -> dict:
    """For the metrics: empty until the first quote builds the model chain."""
    return _controller.breakers if _controller is not None else {}


def get_controller() -> QuoteController:
    """Get or create the QuoteController instance."""
    global _controller
    if _controller is None:
        _controller = QuoteController()
    return _controller


GENERATION_ERRORS = {
    400: {"model": ErrorResponse, "description": "Invalid request parameters"},
    422: {
        "model": ErrorResponse,
        "description": "Invalid request, an instruction in the topic or style, or Gemini refused the topic",
    },
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    502: {
        "model": ErrorResponse,
        "description": "No model returned a quote that passed the checks",
    },
    503: {"model": ErrorResponse, "description": "Every model is rate limited or unavailable"},
    504: {"model": ErrorResponse, "description": "No quote within REQUEST_TIMEOUT"},
}


async def _generate(request: QuoteRequest) -> QuoteResponse:
    trace = Trace(
        category=request.category.value,
        language=request.language,
        length=request.length,
        has_topic=bool(request.topic),
        has_style=bool(request.style),
    )
    started = time.monotonic()
    try:
        response = await get_controller().generate_quote(request, trace)
        trace.outcome = "ok"
        return response
    except (LLMError, GuardrailError) as e:
        trace.outcome, code, message = classify(e)
        logger.warning(f"Generation failed ({trace.outcome}): {e}")
        raise HTTPException(code, message) from e
    except ValueError as e:
        trace.outcome = "invalid"
        logger.error(f"Validation error: {e!s}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        trace.outcome = "error"
        logger.exception("Error generating quote")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quote.",
        ) from e
    finally:
        trace.duration = time.monotonic() - started
        observe(trace)


@router.post(
    "/generate",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a custom quote",
    description="Generate a quote based on specified category, topic, style, and length.",
    responses={200: {"description": "Quote generated successfully"}, **GENERATION_ERRORS},
    dependencies=[Depends(enforce_rate_limit)],
)
async def generate_quote(request: QuoteRequest) -> QuoteResponse:
    return await _generate(request)


@router.get(
    "/random",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a random quote",
    description="Generate a random inspirational quote.",
    responses={200: {"description": "Quote generated successfully"}, **GENERATION_ERRORS},
    dependencies=[Depends(enforce_rate_limit)],
)
async def get_random_quote() -> QuoteResponse:
    return await _generate(QuoteRequest(category=QuoteCategory.RANDOM))


@router.get(
    "/categories",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Get available categories",
    description="Retrieve a list of all available quote categories.",
)
async def get_categories() -> list[str]:
    """
    Get a list of all available quote categories.
    """
    logger.info("Retrieved quote categories")
    return [category.value for category in QuoteCategory]
