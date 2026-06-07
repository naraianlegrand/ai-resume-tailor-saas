"""Schemas for LLM interactions."""

from typing import Optional
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
