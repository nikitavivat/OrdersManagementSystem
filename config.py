import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "orders_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "orders_password")
    DB_NAME: str = os.getenv("DB_NAME", "orders_system")
    
    # Application settings
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache settings
    CACHE_TTL_DEFAULT: int = int(os.getenv("CACHE_TTL_DEFAULT", "300"))  # 5 минут
    CACHE_TTL_NOMENCLATURE: int = int(os.getenv("CACHE_TTL_NOMENCLATURE", "600"))  # 10 минут
    CACHE_TTL_ORDERS: int = int(os.getenv("CACHE_TTL_ORDERS", "60"))  # 1 минута
    
    # Redis settings (для будущего использования)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def is_production(self) -> bool:
        return not self.DEBUG

settings = Settings()
