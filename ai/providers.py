"""AFTERMATH LLM provider configuration."""

import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv()

OTARI_DEFAULT_MODEL = "alibaba/qwen-3.5-35b-a3b"
OTARI_DEFAULT_BASE_URL = "https://api.otari.ai/api/v1"


def get_chat_model(
    provider: str | None = None,
    temperature: float = 0.2,
) -> BaseChatModel:
    """Create a configured chat model."""

    selected = (
        provider or os.getenv("AI_PROVIDER", "gemini")
    ).lower()

    if selected == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        return ChatGoogleGenerativeAI(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-3.5-flash-lite",
            ),
            google_api_key=api_key,
            temperature=temperature,
            max_retries=2,
        )

    if selected == "groq":
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        return ChatGroq(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ),
            api_key=api_key, # type: ignore
            temperature=temperature,
            max_retries=2,
        )

    if selected == "otari":
        api_key = os.getenv("OTARI_API_KEY")

        if not api_key:
            raise ValueError("OTARI_API_KEY is not configured.")

        return ChatOpenAI(
            model=os.getenv(
                "OTARI_MODEL",
                OTARI_DEFAULT_MODEL,
            ),
            api_key=api_key,
            base_url=os.getenv(
                "OTARI_BASE_URL",
                OTARI_DEFAULT_BASE_URL,
            ),
            temperature=temperature,
            max_tokens=6000, # type: ignore
            max_retries=2,
            timeout=120,
            extra_body={
                "reasoning": {
                    "effort": "low",
                }
            },
        )

    raise ValueError(
        f"Unsupported AI provider: {selected}. "
        "Choose gemini, groq, or otari."
    )


def get_provider_status() -> dict[str, dict[str, bool]]:
    """Return provider configuration without exposing credentials."""

    return {
        "gemini": {
            "configured": bool(os.getenv("GEMINI_API_KEY")),
            "model_configured": bool(
                os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
            ),
        },
        "groq": {
            "configured": bool(os.getenv("GROQ_API_KEY")),
            "model_configured": bool(
                os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
            ),
        },
        "otari": {
            "configured": bool(os.getenv("OTARI_API_KEY")),
            "model_configured": bool(
                os.getenv("OTARI_MODEL", OTARI_DEFAULT_MODEL)
            ),
        },
    }