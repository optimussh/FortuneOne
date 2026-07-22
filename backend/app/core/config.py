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

    # Payments: mock | toss
    # mock = always testable without keys; toss = sandbox/live when keys set
    PAYMENT_PROVIDER: str = "mock"
    PAYMENT_TEST_MODE: bool = True  # True: never charge real money path without live keys

    # Toss Payments (https://developers.tosspayments.com/)
    # Test keys: test_ck_... / test_sk_...  Live: live_ck_... / live_sk_...
    TOSS_CLIENT_KEY: Optional[str] = None
    TOSS_SECRET_KEY: Optional[str] = None
    TOSS_WEBHOOK_SECRET: Optional[str] = None  # optional future

    # Business disclosure (shown on site; fill when ready)
    BUSINESS_NAME: str = "FortuneOne"
    BUSINESS_CEO: str = "[대표자명]"
    BUSINESS_NUMBER: str = "[사업자등록번호]"
    BUSINESS_MAIL_ORDER: str = "[통신판매업 신고번호]"
    BUSINESS_ADDRESS: str = "[사업장 주소]"
    BUSINESS_PHONE: str = "[고객센터 전화]"
    BUSINESS_EMAIL: str = "support@fortuneone.local"

    # OAuth (social login)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    KAKAO_CLIENT_ID: Optional[str] = None
    KAKAO_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
