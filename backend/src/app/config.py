from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "users"
    
    # JWT
    SECRET_KEY: str = "4a8c9e7b2f3c1d6a8f4d5e6f7a8b9c0d1e2f5b4c9d7e2f1a3b6c8d9e0f1a2b3c"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "dynamix.services.entreprise@gmail.com"
    SMTP_PASSWORD: str = "mgnv lkei lxce snlw"
    FROM_EMAIL: str = "dynamix.services.entreprise@gmail.com"
    
    # Admin settings
    RESET_CODE_EXPIRY_MINUTES: int = 15
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()