"""Configuration settings for the FastAPI Sales Analytics application."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    # SECURITY: API key must be set via environment variable
    # No default value for security - application will fail to start if not provided
    # Required - must be set in .env file
    API_KEY: str
    API_KEY_HEADER: str
    
    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    
    # CORS Configuration
    # IMPORTANT: CORS (Cross-Origin Resource Sharing) must be properly configured
    # for security reasons and to ensure the application runs smoothly with frontend clients.
    # 
    # SECURITY: Default is empty list [] - you MUST explicitly configure allowed origins
    # - For development: Set CORS_ORIGINS=["*"] in .env (less secure, convenient for testing)
    # - For production: Set specific origins (e.g., CORS_ORIGINS=["https://yourdomain.com"])
    # - Allowing "*" permits any origin, which is insecure for production
    # - Proper CORS configuration prevents unauthorized cross-origin requests
    CORS_ORIGINS: List[str]
    
    # Allow credentials (cookies, authorization headers) in cross-origin requests
    # Set to False if you don't need to send credentials
    CORS_ALLOW_CREDENTIALS: bool
    
    # Allowed HTTP methods for cross-origin requests
    # Default ["*"] allows all methods (GET, POST, PUT, DELETE, etc.)
    # Restrict to specific methods in production (e.g., ["GET", "POST"])
    CORS_ALLOW_METHODS: List[str]

    # Allowed headers in cross-origin requests
    # Default ["*"] allows all headers
    # In production, specify only required headers for better security
    CORS_ALLOW_HEADERS: List[str]
    
    # Logging
    LOG_LEVEL: str
    
    # File Upload Configuration
    # SECURITY: Maximum file size in bytes to prevent DoS attacks via large file uploads
    # Default: 10MB (10 * 1024 * 1024 bytes)
    # Adjust based on your needs, but keep reasonable limits for security
    MAX_FILE_SIZE: int
    
    class Config:
        env_file = ".env"
        env_files = [".env", ".env.example"]
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
