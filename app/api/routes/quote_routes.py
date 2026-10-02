import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.controllers import QuoteController
from app.api.models import ErrorResponse, QuoteCategory, QuoteRequest, QuoteResponse
from app.api.utils.rate_limit import enforce_rate_limit


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

# Lazy initialization of controller
_controller = None


def get_controller() -> QuoteController:
    """Get or create the QuoteController instance."""
    global _controller
    if _controller is None:
        _controller = QuoteController()
    return _controller


GENERATION_ERRORS = {
    400: {"model": ErrorResponse, "description": "Invalid request parameters"},
    422: {"model": ErrorResponse, "description": "Invalid request, or Gemini refused the topic"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    502: {"model": ErrorResponse, "description": "Gemini returned an error or no quote"},
    503: {"model": ErrorResponse, "description": "Gemini quota exhausted"},
    504: {"model": ErrorResponse, "description": "Gemini timed out"},
}


async def _generate(request: QuoteRequest) -> QuoteResponse:
    try:
        return await get_controller().generate_quote(request)
    except HTTPException:
        raise  # already carries a status and a message that is safe to show
    except ValueError as e:
        logger.error(f"Validation error: {e!s}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.exception("Error generating quote")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quote.",
        ) from e


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
    logger.info(f"Received quote generation request: {request.model_dump()}")
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
    logger.info("Received random quote request")
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
