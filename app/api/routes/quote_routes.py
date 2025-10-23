"""
API routes for quote generation.
"""
from fastapi import APIRouter, HTTPException, status
from app.api.models import QuoteRequest, QuoteResponse, ErrorResponse, QuoteCategory
from app.api.controllers import QuoteController

router = APIRouter(prefix="/api/quotes", tags=["quotes"])
controller = QuoteController()


@router.post(
    "/generate",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a custom quote",
    description="Generate a quote based on specified category, topic, style, and length.",
    responses={
        200: {"description": "Quote generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def generate_quote(request: QuoteRequest) -> QuoteResponse:
    """
    Generate a custom quote based on the provided parameters.
    
    - **category**: Category of the quote (motivation, inspiration, wisdom, etc.)
    - **topic**: Optional specific topic for the quote
    - **style**: Optional writing style (e.g., 'Shakespeare', 'modern', 'philosophical')
    - **length**: Desired length: 'short', 'medium', or 'long'
    """
    try:
        return await controller.generate_quote(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
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
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_random_quote() -> QuoteResponse:
    """
    Generate a random inspirational quote.
    """
    try:
        return await controller.get_random_quote()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
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
    return [category.value for category in QuoteCategory]
