"""Schemas for LLM interactions."""

from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Schema for LLM text generation request."""

    prompt: str = Field(
        ...,
        description="The prompt text to send to the LLM"
    )
    provider: Optional[str] = Field(
        "mock",
        description="The LLM provider to use: 'mock', 'openai', or 'gemini'"
    )
    system_instruction: Optional[str] = Field(
        None,
        description="Optional system prompt or instructions to guide the model behavior"
    )


class GenerateResponse(BaseModel):
    """Schema for LLM text generation response."""

    provider: str = Field(
        ...,
        description="The LLM provider used for generation"
    )
    response: str = Field(
        ...,
        description="The generated text response from the model"
    )


class TailorRequest(BaseModel):
    """Schema for resume tailoring input request."""

    resume_text: str = Field(
        ...,
        description="The extracted raw text from the user's resume"
    )
    job_description: str = Field(
        ...,
        description="The target job description to analyze the resume against"
    )
    provider: Optional[str] = Field(
        "mock",
        description="The LLM provider to use: 'mock', 'openai', or 'gemini'"
    )


class TailorResponse(BaseModel):
    """Schema for structured resume tailoring results."""

    match_score: int = Field(
        ...,
        description="Simulated ATS match score between 0 and 100, where 100 is a perfect match",
        ge=0,
        le=100
    )
    missing_keywords: List[str] = Field(
        ...,
        description="Critical keywords found in the job description but missing or underrepresented in the resume"
    )
    tailored_bullet_points: List[str] = Field(
        ...,
        description="Exactly three tailored bullet points incorporating missing keywords and matching the job description"
    )
