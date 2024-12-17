from typing import Any
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

class Settings(BaseSettings):
    PROJECT_NAME: str
    ALLOWED_ORIGINS: str
    LOG_FILE: str
    MONGODB_URL: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    MONGODB_DB_NAME: str = "flight"
    MONGODB_USER: str = "admin"
    MONGODB_PASSWORD: str = "admin"
    # Flightio API Settings
    FLIGHTIO_API_KEY: str = "675d3f17ac6016bffe232fba"
    FLIGHTIO_BASE_URL: str = "https://api.flightapi.io"
    
    # Flightio Database Settings
    FLIGHTIO_MONGO_COLLECTION: str = "flight_schedules"
    FLIGHTIO_REDIS_TTL: int = 3600  # 1 hour in seconds

    # Flight Search Cache Settings
    FLIGHT_SEARCH_CACHE_KEY: str = "flight_search"
    FLIGHT_SEARCH_CACHE_EXPIRY: int = 3600  # 1 hour in seconds

    class Config:
        env_file = ("builder/.env", ".env")  # Try multiple possible locations
        env_file_encoding = 'utf-8'
        case_sensitive = True
        env_prefix = ""  

    def check_not_empty(self) -> None:
        """Validate all fields are not empty after model initialization"""
        for field_name, field_value in self:
            logging.info(f"Checking field {field_name} with value {field_value}")
            if not field_value or (isinstance(field_value, str) and field_value.strip() == ""):
                raise ValueError(f"Field {field_name} cannot be empty")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # Convert ALLOWED_ORIGINS string to list
    settings.ALLOWED_ORIGINS = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(',')]
    settings.check_not_empty()
    return settings

# Create settings instance
settings = get_settings()
