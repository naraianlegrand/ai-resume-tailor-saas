"""FastAPI application entrypoint and HTTP controllers."""

import logging
from typing import Dict

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form

from mangum import Mangum

from app.models.llm import GenerateRequest, GenerateResponse, TailorResponse
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService

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


@app.post("/api/v1/tailor", response_model=TailorResponse, status_code=status.HTTP_200_OK)
async def tailor_resume(
    file: UploadFile = File(..., description="The PDF resume file to tailor"),
    job_description: str = Form(..., description="Target job description text"),
    provider: str = Form("mock", description="LLM provider: 'mock', 'openai', or 'gemini'")
) -> TailorResponse:
    """Extracts text from a PDF resume and tailors it to match a job description.

    Args:
        file: Uploaded PDF resume.
        job_description: Target job description.
        provider: Selected LLM provider.

    Returns:
        TailorResponse with ATS score, missing keywords, and tailored bullet points.

    Raises:
        HTTPException: 400 if PDF parsing or provider fails, 500 on internal error.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )

    try:
        # Read the file bytes
        file_bytes = await file.read()

        # Extract text from the PDF
        resume_text = ParserService.extract_text_from_pdf(file_bytes)

        # Call LLM service to analyze and tailor the resume
        llm_service = LLMService(provider=provider)
        tailoring_result = await llm_service.tailor_resume(
            resume_text=resume_text,
            job_description=job_description
        )
        return tailoring_result

    except ValueError as val_err:
        logger.warning("Value error during resume tailoring: %s", str(val_err))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        logger.error(
            "Unhandled error during resume tailoring: %s",
            str(exc),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during resume tailoring processing."
        )
    finally:
        await file.close()


# AWS Lambda Handler
handler = Mangum(app)
