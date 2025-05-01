"""
Configuration settings for the application.
Uses pydantic-settings for environment variable loading and validation.
"""
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Optional, Union


class Settings(BaseSettings):
    """Application settings."""
    
    # Project metadata
    PROJECT_NAME: str = "NewsMonitor"
    PROJECT_DESCRIPTION: str = "A SaaS application for monitoring news and media mentions"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API settings
    API_PREFIX: str = "/api/v1"
    BASE_URL: str = "http://localhost:8000"
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Use a plain list of strings (not AnyHttpUrl which might be causing issues)
    CORS_ORIGINS: List[str] = []

    # Set model configuration to disable field checking
    model_config = {
        "validate_default": False
    }
    
    # Rate limiting
    RATE_LIMIT: int = 100  # requests
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # LLM settings
    LLM_PROVIDER: str = "openai"  # openai, claude, gemini
    LLM_MODEL: str = "gpt-4"  # model name, depends on provider
    
    # API keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Email settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_SENDER: str = "noreply@newsmonitor.ai"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get the CORS origins as a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        origins = []
        for origin in self.CORS_ORIGINS.split(","):
            origin = origin.strip()
            if origin:
                origins.append(origin)
        return origins

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        """Assemble database URI from components."""
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),
            path=f"{values.data.get('POSTGRES_DB', '')}"
        )

        
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod  # Required for Pydantic v2 validators
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v:
            return []
            
        if isinstance(v, str):
            # Handle comma-separated format
            if "," in v:
                return [i.strip() for i in v.split(",")]
                
            # Single URL
            return [v.strip()]
            
        if isinstance(v, list):
            return v
            
        return []
    
    # V2 configuration format
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()