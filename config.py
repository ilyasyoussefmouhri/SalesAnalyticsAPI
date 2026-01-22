"""Configuration settings for the FastAPI Sales Analytics application."""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_key: str = "your-secret-api-key-change-in-production"
    api_key_header: str = "X-API-Key"
    
    # Application
    app_name: str = "FastAPI Sales Analytics"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
