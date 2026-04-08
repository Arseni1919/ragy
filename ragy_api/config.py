from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TAVILY_API_KEY: str
    HF_EMB_MODEL: str = "all-MiniLM-L6-v2"
    HF_TOKEN: str | None = None
    OLLAMA_EMB_MODEL: str = "nomic-embed-text"
    DB_PATH: str = "./ragy_db"
    DB_PROVIDER: str = "zvec"  # Options: "chromadb", "zvec"
    RAGY_MAX_CONCURRENT: int = 3

    BRIGHT_DATA_API_KEY: str | None = None
    BRIGHT_DATA_ZONE: str | None = None
    BRIGHTDATA_BROWSERAPI_USERNAME: str | None = None
    BRIGHTDATA_BROWSERAPI_PASSWORD: str | None = None

    GEMINI_API_KEY: str | None = None
    LLM_MODEL: str = "gemini/gemini-2.5-flash-lite"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HOUR: int = 2
    SCHEDULER_TIMEZONE: str = "UTC"
    JOBS_DB_PATH: str = "./ragy_jobs.db"

    class Config:
        env_file = ".env"


settings = Settings()
