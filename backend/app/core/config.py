from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FortuneOne"
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database — local default: SQLite file (회원가입·프로필 저장)
    # Postgres example: postgresql+asyncpg://user:password@localhost:5432/saasdb
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/fortuneone.db"
    
    # External APIs
    RESEND_API_KEY: Optional[str] = None
    
    FRONTEND_URL: str = "http://localhost:6100"

    # Toss Payments
    TOSS_CLIENT_KEY: Optional[str] = None
    TOSS_SECRET_KEY: Optional[str] = None

    # OAuth (social login)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    KAKAO_CLIENT_ID: Optional[str] = None
    KAKAO_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
