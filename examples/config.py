from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TAVILY_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_MODEL_NAME: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"


settings = Settings()
