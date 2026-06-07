"""Service module for LLM providers."""

import json
import logging
import os
from typing import Optional

import httpx
import openai

from app.models.llm import TailorResponse

logger = logging.getLogger(__name__)


class LLMService:
    """Service to abstract LLM interactions, supporting OpenAI, Gemini, and Mock providers."""

    def __init__(self, provider: str = "mock", api_key: Optional[str] = None) -> None:
        """Initializes the LLM Service with a specified provider.

        Args:
            provider: The name of the LLM provider ('openai', 'gemini', or 'mock').
            api_key: Optional API key. If not provided, it will look up env variables.
        """
        self.provider = provider.lower()
        
        # Read API key based on provider if not explicitly passed
        if api_key:
            self.api_key = api_key
        else:
            if self.provider == "gemini":
                self.api_key = os.environ.get("GEMINI_API_KEY")
            elif self.provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            else:
                self.api_key = None

        logger.info(
            "Initializing LLMService with provider: %s (API key present: %s)", 
            self.provider, 
            self.api_key is not None
        )

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates text based on a prompt and optional system instructions (legacy method).

        Args:
            prompt: The user prompt to generate text for.
            system_instruction: Optional system level instructions to guide the model.

        Returns:
            The generated text response.

        Raises:
            ValueError: If an unsupported provider is specified.
            Exception: For errors during API execution.
        """
        try:
            if self.provider == "mock":
                return f"[Mock LLM Response] Prompt: {prompt}"

            elif self.provider == "openai":
                client = openai.OpenAI(api_key=self.api_key)
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                return response.choices[0].message.content or ""

            elif self.provider == "gemini":
                logger.info("Executing Gemini text generation via raw HTTP REST bypass")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
                
                async with httpx.AsyncClient() as http_client:
                    http_resp = await http_client.post(url, json=payload, timeout=60.0)
                    if http_resp.status_code != 200:
                        raise ValueError(f"Gemini REST API error {http_resp.status_code}: {http_resp.text}")
                    
                    resp_json = http_resp.json()
                    return resp_json["candidates"][0]["content"]["parts"][0]["text"]

            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

        except Exception as exc:
            logger.error(
                "Error generating text with provider %s: %s",
                self.provider,
                str(exc),
                exc_info=True
            )
            raise exc

    async def tailor_resume(self, resume_text: str, job_description: str) -> TailorResponse:
        """Analyzes a resume against a job description using structured LLM outputs.

        Args:
            resume_text: Raw text of the candidate's resume.
            job_description: Target job description.

        Returns:
            TailorResponse containing ATS score, missing keywords, and tailored bullet points.

        Raises:
            ValueError: If an unsupported provider is specified.
            Exception: For errors during API execution or parsing.
        """
        system_prompt = (
            "You are an expert ATS (Applicant Tracking System) optimizer and professional resume writer.\n"
            "Your task is to analyze the candidate's resume text against the target job description and perform the following:\n"
            "1. Calculate a simulated ATS match score (0 to 100) based on alignment of skills, experience, and qualifications.\n"
            "2. Identify missing critical keywords, specific job qualifications, certifications, or tools (for example: engineering qualifications like SCADA, PLC, AutoCAD, or specific technical tools and methodologies if they are present in the job description) that are absent or underrepresented in the resume.\n"
            "3. Write exactly three tailored, high-impact bullet points for the resume that integrate these missing critical keywords/qualifications naturally and align perfectly with the job description. Each bullet point must follow the STAR methodology (Situation, Task, Action, Result) or Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]).\n"
            "\n"
            "You must return the result in a valid JSON object matching the requested schema."
        )

        user_prompt = (
            f"Resume Text:\n{resume_text}\n\n"
            f"Job Description:\n{job_description}"
        )

        try:
            if self.provider == "mock":
                # Mocked structured response
                logger.info("Generating mock structured resume tailoring response")
                return TailorResponse(
                    match_score=75,
                    missing_keywords=["AWS Lambda", "FastAPI", "Serverless Architecture"],
                    tailored_bullet_points=[
                        "Designed and deployed a high-scale serverless API using FastAPI and AWS Lambda, reducing endpoint latency by 35%.",
                        "Implemented strict Pydantic schemas and input validation, decreasing runtime payload errors by 50% across 3 major services.",
                        "Integrated OpenAI and Google GenAI SDKs into existing Python applications, enabling automated content moderation at scale."
                    ]
                )

            elif self.provider == "openai":
                logger.info("Executing OpenAI structured output API request")
                # Initialize client safely to fall back to environment variables if self.api_key is None
                client = openai.OpenAI(api_key=self.api_key) if self.api_key else openai.OpenAI()
                response = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=TailorResponse
                )
                parsed = response.choices[0].message.parsed
                if not parsed:
                    raise ValueError("Failed to parse structured output from OpenAI.")
                return parsed

            elif self.provider == "gemini":
                logger.info("Executing Gemini structured output via raw HTTP REST bypass")
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_prompt}]},
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "OBJECT",
                            "properties": {
                                "match_score": {"type": "INTEGER"},
                                "missing_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "tailored_bullet_points": {"type": "ARRAY", "items": {"type": "STRING"}}
                            },
                            "required": ["match_score", "missing_keywords", "tailored_bullet_points"]
                        }
                    }
                }
                
                async with httpx.AsyncClient() as http_client:
                    http_resp = await http_client.post(url, json=payload, timeout=60.0)
                    if http_resp.status_code != 200:
                        raise ValueError(f"Gemini REST API error {http_resp.status_code}: {http_resp.text}")
                    
                    resp_json = http_resp.json()
                    text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                parsed_data = json.loads(text_content.strip())
                return TailorResponse(**parsed_data)

            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

        except ValueError as val_err:
            logger.warning("Validation or setup error in LLMService: %s", str(val_err))
            raise val_err
        except Exception as exc:
            logger.error(
                "Error tailoring resume with provider %s: %s",
                self.provider,
                str(exc),
                exc_info=True
            )
            raise exc
