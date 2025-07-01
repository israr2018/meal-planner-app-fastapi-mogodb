# app/config.py
# from pydantic import BaseSettings
# from pydantic import BaseSettings  ❌ old
from pydantic_settings import BaseSettings  # ✅ new


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    db_name: str = "meal_planner"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()