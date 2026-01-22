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
    
    # CORS Configuration
    # IMPORTANT: CORS (Cross-Origin Resource Sharing) must be properly configured
    # for security reasons and to ensure the application runs smoothly with frontend clients.
    # 
    # Security considerations:
    # - In production, replace ["*"] with specific allowed origins (e.g., ["https://yourdomain.com"])
    # - Allowing "*" permits any origin, which is convenient for development but insecure for production
    # - Proper CORS configuration prevents unauthorized cross-origin requests
    cors_origins: List[str] = ["*"]
    
    # Allow credentials (cookies, authorization headers) in cross-origin requests
    # Set to False if you don't need to send credentials
    cors_allow_credentials: bool = True
    
    # Allowed HTTP methods for cross-origin requests
    # Default ["*"] allows all methods (GET, POST, PUT, DELETE, etc.)
    # Restrict to specific methods in production (e.g., ["GET", "POST"])
    cors_allow_methods: List[str] = ["*"]
    
    # Allowed headers in cross-origin requests
    # Default ["*"] allows all headers
    # In production, specify only required headers for better security
    cors_allow_headers: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
