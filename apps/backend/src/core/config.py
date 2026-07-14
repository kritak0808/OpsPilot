import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OpsPilot AI Core"
    API_VERSION: str = "v1"
    
    # Environment
    ENV: str = "development"
    
    # Databases
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opspilot"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Telemetry
    OTEL_SERVICE_NAME: str = "opspilot-core"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
