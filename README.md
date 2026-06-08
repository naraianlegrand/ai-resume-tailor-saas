# Serverless AI Resume Tailor SaaS API

A high-performance, cloud-native microservice API built with Python and FastAPI designed to automate semantic gap analysis for job seekers. This backend engine ingests a binary PDF resume, strips the raw text data using optimized serverless-safe parsing utilities, and executes an asynchronous evaluation against a target job description using an advanced HTTP REST protocol. 

Rather than returning unpredictable text, the system utilizes raw REST-driven JSON schema validation to guarantee a strict, production-ready response payload containing automated ATS tracking scores, missing industry keywords, and tailored bullet points structured via Google's XYZ formula.

---

## Tech Stack & Keywords Gained

* **Language & Core:** Python 3.12, Asynchronous Programming (`asyncio`)
* **Web Framework:** FastAPI, Uvicorn, Pydantic (Strict Data Validation)
* **Networking Layer:** HTTPX (Asynchronous REST API Routing)
* **Data Parsing:** PyPDF (Pure-Python serverless-optimized extraction)
* **Cloud Architecture & Containers:** Docker, Mangum (AWS Lambda Serverless Adapter)

---

## The Engineering Edge: Solving the SDK Sandbox Bottleneck

During local development within an isolated IDE sandbox environment, the system hit a major operational roadblock: the standard Google GenAI SDK threw low-level operating system errors (`[Errno 13] Permission denied`) by attempting to write dynamic telemetry execution logs to a locked local volume partition (`\\?\Volume...`). 

### The Senior Engineer Pivot:
Instead of spending hours fighting sandbox infrastructure or adding brittle logging configurations, I engineered a high-performance workaround. I stripped out the heavy SDK entirely and built a **direct asynchronous HTTP REST client using HTTPX** to communicate directly with the Gemini 2.5 Flash API endpoints. 

This design choice completely bypassed the filesystem write bottleneck, eliminated bloated external library dependencies, and drastically minimized the application's memory footprint—making the codebase faster, lighter, and completely optimized for strict, read-only serverless cloud environments like **AWS Lambda**.

---

## Live Output Showcase (The Reality Check)

Below is an authentic end-to-end transaction captured directly from the live FastAPI local server endpoint (`POST /api/v1/tailor`), testing a Software Engineering background against a real-world Automation/Telecommunications Internship description in Montreal (requiring heavy industrial automation like SCADA, PLCs, and AutoCAD). 

### Sample Target Job Description Input:
> *"Within the Telecommunications team, as an Intern, your responsibilities include supporting the programming of programmable logic controllers (RTU, PLC, etc.), participating in the design of centralized control centers for SCADA management systems, and preparing drawings in AutoCAD..."*

### Pristine Structured JSON Output Received (200 OK):
```json
{
  "match_score": 48,
  "missing_keywords": [
    "PLC",
    "RTU",
    "SCADA",
    "AutoCAD",
    "Telecommunications",
    "ISO"
  ],
  "tailored_bullet_points": [
    "Applied Python automation expertise to develop control logic simulations and data acquisition workflows, demonstrating readiness to support programming of programmable logic controllers (PLCs) and integration within SCADA management systems.",
    "Translated complex engineering requirements into clear technical designs, building foundational skills in interpreting specifications for telecommunications infrastructure projects and preparing for drawing generation using tools like AutoCAD.",
    "Contributed to project lifecycle management by preparing comprehensive progress reports and technical documentation, ensuring solutions met stringent quality standards and client specifications within a telecommunications context, drawing from agile development practices."
  ]
  
}
```

*Note: The highly accurate match score of 48% demonstrates the semantic accuracy of the system, flagging the missing hardware domain expertise while dynamically crafting transferable software engineering bridge points without fabricating false experience.*

---

## 📂 Project Architecture

```text
ai-resume-tailor-saas/
├── app/
│   ├── main.py                # FastAPI engine & Mangum Serverless Handler
│   ├── models/
│   │   └── llm.py             # Pydantic structured schema definitions
│   └── services/
│       ├── parser_service.py  # Pure-Python serverless PDF extraction
│       └── llm_service.py     # Custom HTTPX asynchronous REST connection
├── docker/
│   └── Dockerfile.lambda      # AWS Lambda deployment container configuration
├── tests/
│   └── test_api.py            # Local validation unit test suite
├── .env.example               # Secure configuration template
└── requirements.txt           # Application dependencies
```

---

## ⚡ Local Quickstart

### 1. Clone and Setup Environment
```bash
git clone [https://github.com/yourusername/ai-resume-tailor-saas.git](https://github.com/yourusername/ai-resume-tailor-saas.git)
cd ai-resume-tailor-saas
python -m venv .venv
# On Windows PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Credentials
Create a local `.env` file in the root directory:
```text
GEMINI_API_KEY=your_production_api_key_here
```

### 3. Launch Interactive Swagger Interface
```bash
uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to interactively test binary file payloads directly inside the browser.

---

## 📦 Production Containerization (AWS Lambda Architecture)

To deploy this backend as an enterprise-grade serverless function, the application is packed inside a specialized Docker container optimized for the AWS Lambda Linux environment. 

The complete blueprint is maintained inside `docker/Dockerfile.lambda`:

```dockerfile
# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Copy the dependency matrix file into the container task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install all runtime dependencies directly into the root execution directory
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire modular application directory structure
COPY app/ ${LAMBDA_TASK_ROOT}/app

# Set the execution target to route all incoming HTTP payloads through the Mangum handler
CMD [ "app.main.handler" ]
```
