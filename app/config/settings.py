from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):

    # Vector Database

    # qdrant_host: str = "localhost"
    # qdrant_port: int = 6333

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    collection_name: str
    database_url: str = "sqlite:///./data/app.db"

    # Embedding

    embedding_model: str

    # LLM

    llm_provider: str = "openrouter"
    # llm_provider: str = "groq"
    llm_model: str

    openrouter_api_key: str | None = None
    # groq_api_key: str | None = None

    gemini_api_key: str

    # Authentication

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Retrieval

    search_mode: str = "semantic"
    top_k: int = 5

    # Chunking

    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Logging

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    query_cache_ttl_seconds: int = 300

settings = Settings()