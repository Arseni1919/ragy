from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TAVILY_API_KEY: str
    GEMINI_API_KEY: str
    HF_EMB_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_EMB_MODEL: str = "nomic-embed-text"
    DB_PATH: str = "./ragy_db"
    RAGY_MAX_CONCURRENT: int = 10
    LLM_MODEL: str = "gemini/gemini-2.5-flash-lite"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HOUR: int = 2
    SCHEDULER_TIMEZONE: str = "UTC"

    class Config:
        env_file = ".env"


settings = Settings()
