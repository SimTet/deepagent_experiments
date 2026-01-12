from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(extra="allow", env_file=".env", env_file_encoding="utf-8")

    TAVILY_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.0
    MAX_CONCURRENT_RESEARCH_UNITS: int = 3
    MAX_RESEARCHER_ITERATIONS: int = 5


settings = Settings()
