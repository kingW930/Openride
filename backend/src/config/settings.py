"""
Configuration settings for OpenRide backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "OpenRide API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - SQLite for demo (no setup required)
    DATABASE_URL: str = "sqlite:///./openride_demo.db"
    
    # Security
    JWT_SECRET_KEY: str = "demo-secret-key-change-in-production-openride-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for demo
    
    # Interswitch Payment Gateway (QA/Test Environment)
    INTERSWITCH_MERCHANT_CODE: str = "MX007"
    INTERSWITCH_PAY_ITEM_ID: str = "101007"
    INTERSWITCH_API_KEY: str = ""
    INTERSWITCH_PAYMENT_URL: str = "https://newwebpay.qa.interswitchng.com/collections/w/pay"
    INTERSWITCH_QUERY_URL: str = "https://qa.interswitchng.com/collections/api/v1/gettransaction.json"
    INTERSWITCH_MODE: str = "TEST"
    
    # Blockchain Configuration
    BLOCKCHAIN_NETWORK: str = "demo-blockchain"
    BLOCKCHAIN_ENABLED: bool = True
    
    # CORS - Allow frontend access
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    # AI Route Matching
    AI_MATCHING_THRESHOLD: float = 0.75
    MAX_ROUTE_DISTANCE_KM: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
