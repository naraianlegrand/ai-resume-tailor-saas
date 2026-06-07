"""FastAPI application entrypoint and HTTP controllers."""

import logging
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from mangum import Mangum

from app.models.llm import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Serverless FastAPI Application",
    description="A serverless FastAPI app running on AWS Lambda with LLM integrations.",
    version="1.0.0"
)


@app.get("/", status_code=status.HTTP_200_OK)
def read_root() -> Dict[str, str]:
    """Health check endpoint to verify the API is running.

    Returns:
        A dictionary containing the status and service name.
    """
    return {"status": "healthy", "service": "Serverless FastAPI Application"}


@app.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_200_OK)
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    """Generate text using the specified LLM provider.

    Args:
        request: The generation request parameters.

    Returns:
        GenerateResponse with the generated content and provider.

    Raises:
        HTTPException: 400 if the provider is unsupported, or 500 on internal errors.
    """
    try:
        llm_service = LLMService(provider=request.provider)
        response_text = await llm_service.generate_text(
            prompt=request.prompt,
            system_instruction=request.system_instruction
        )
        return GenerateResponse(
            provider=request.provider,
            response=response_text
        )
    except ValueError as val_err:
        logger.warning("Invalid provider requested: %s", str(val_err))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        logger.error(
            "Unhandled exception during generation: %s",
            str(exc),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while communicating with the LLM provider."
        )


# AWS Lambda Handler
handler = Mangum(app)
