from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings
from langchain_google_genai import ChatGoogleGenerativeAI


class Settings(BaseSettings):
    model_config = ConfigDict(extra="allow", env_file=".env", env_file_encoding="utf-8")

    TAVILY_API_KEY: str = ""
    GOOGLE_API_KEY: str
    GOOGLE_MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.0
    MAX_CONCURRENT_RESEARCH_UNITS: int = 3
    MAX_RESEARCHER_ITERATIONS: int = 5

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def _require_non_empty(cls, value: str, info) -> str:
        if not value.strip():
            raise ValueError(
                f"{info.field_name} is empty. Edit .env (copied from .env_example) "
                f"and set a real value for {info.field_name}."
            )
        return value


settings = Settings()


def create_gemini_model() -> ChatGoogleGenerativeAI:
    """Build the Gemini client with credentials from the validated settings."""
    return ChatGoogleGenerativeAI(
        model=settings.GOOGLE_MODEL_NAME,
        temperature=settings.TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY,
    )
