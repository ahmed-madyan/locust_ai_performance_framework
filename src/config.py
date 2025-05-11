from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Locust Settings
    LOCUST_HOST: str = "http://localhost:8000"
    LOCUST_USERS: int = 10
    LOCUST_SPAWN_RATE: int = 1
    LOCUST_RUN_TIME: str = "1m"
    
    # InfluxDB Settings
    INFLUXDB_URL: Optional[str] = None
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: Optional[str] = None
    INFLUXDB_BUCKET: Optional[str] = None
    
    # Redis Settings (for Celery)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "locust_framework.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 