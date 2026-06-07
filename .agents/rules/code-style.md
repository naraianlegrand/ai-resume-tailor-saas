---
trigger: always_on
---

# Engineering Code Style Guide

* **Architecture:** Maintain strict separation of concerns. HTTP controllers belong in `app/main.py`, domain business logic belongs in `app/services/`, and schemas belong in `app/models/`.
* **Standards:** Follow PEP 8 formatting rules implicitly. All functions must contain descriptive docstrings and strict type hinting.
* **LLM Agnostic:** Abstract the LLM interface into a service class (`LLMService`) so we can toggle between OpenAI and Gemini seamlessly.
* **Error Handling:** Use explicit try-except blocks with clean logging instead of bare exception handling.