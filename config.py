"""Configuration settings for the FastAPI Sales Analytics application."""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    # SECURITY: API key must be set via environment variable
    # No default value for security - application will fail to start if not provided
    api_key: str  # Required - must be set in .env file
    api_key_header: str = "X-API-Key"
    
    # Application
    app_name: str = "FastAPI Sales Analytics"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS Configuration
    # IMPORTANT: CORS (Cross-Origin Resource Sharing) must be properly configured
    # for security reasons and to ensure the application runs smoothly with frontend clients.
    # 
    # SECURITY: Default is empty list [] - you MUST explicitly configure allowed origins
    # - For development: Set CORS_ORIGINS=["*"] in .env (less secure, convenient for testing)
    # - For production: Set specific origins (e.g., CORS_ORIGINS=["https://yourdomain.com"])
    # - Allowing "*" permits any origin, which is insecure for production
    # - Proper CORS configuration prevents unauthorized cross-origin requests
    cors_origins: List[str] = []  # SECURITY: Empty by default - must be explicitly configured
    
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
    
    # File Upload Configuration
    # SECURITY: Maximum file size in bytes to prevent DoS attacks via large file uploads
    # Default: 10MB (10 * 1024 * 1024 bytes)
    # Adjust based on your needs, but keep reasonable limits for security
    max_file_size: int = 10 * 1024 * 1024  # 10MB default
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
