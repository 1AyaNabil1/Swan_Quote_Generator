from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.api.models import QuoteRequest, QuoteResponse, ErrorResponse, QuoteCategory
from app.api.controllers import QuoteController
import logging
import redis.asyncio as redis
from app.config import settings

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

# Initialize rate limiter (only if Redis is configured)
async def init_rate_limiter():
    """Initialize rate limiter - disabled on Vercel serverless."""
    # Skip Redis on serverless environments
    logger.info("Rate limiter disabled for serverless deployment")
    return

# Rate limiter dependency (10 requests per minute)
rate_limiter = RateLimiter(times=10, seconds=60) if settings.debug else RateLimiter(times=10, seconds=60)

@router.post(
    "/generate",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a custom quote",
    description="Generate a quote based on specified category, topic, style, and length.",
    responses={
        200: {"description": "Quote generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
    # Temporarily disabled rate limiting
    # dependencies=[Depends(rate_limiter)] if settings.debug else [Depends(rate_limiter)]
)
async def generate_quote(request: QuoteRequest) -> QuoteResponse:
    try:
        logger.info(f"Received quote generation request: {request.model_dump()}")
        controller = get_controller()
        return await controller.generate_quote(request)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating quote: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quote: {str(e)}"
        )


@router.get(
    "/random",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a random quote",
    description="Generate a random inspirational quote.",
    responses={
        200: {"description": "Quote generated successfully"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_random_quote() -> QuoteResponse:
    try:
        logger.info("Received random quote request")
        controller = get_controller()
        return await controller.get_random_quote()
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating random quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quote: {str(e)}"
        )


@router.get(
    "/categories",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Get available categories",
    description="Retrieve a list of all available quote categories."
)
async def get_categories() -> list[str]:
    """
    Get a list of all available quote categories.
    """
    logger.info("Retrieved quote categories")
    return [category.value for category in QuoteCategory]
