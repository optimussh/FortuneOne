from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api import auth, fortune, profiles, engagement, journal
from app.core.database import engine, async_session_maker
from app.core.security import get_password_hash
from app.models.base import SQLModel
from app.models.user import User
from app.models.fortune_profile import FortuneProfile  # noqa: F401
from app.models import engagement as engagement_models  # noqa: F401
from sqlmodel import select

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    # Seed local demo accounts (never block startup)
    try:
        from datetime import date
        from app.models.fortune_profile import FortuneProfile

        seeds = [
            {
                "email": "admin@fortuneone.local",
                "password": "admin1234",
                "full_name": "Admin",
                "is_superuser": True,
                "solar_date": date(1990, 1, 1),
                "gender": "male",
            },
            {
                "email": "test@fortuneone.local",
                "password": "test1234",
                "full_name": "Test User",
                "is_superuser": False,
                "solar_date": date(1995, 6, 15),
                "gender": "female",
            },
        ]
        async with async_session_maker() as session:
            for s in seeds:
                result = await session.exec(select(User).where(User.email == s["email"]))
                user = result.first()
                if not user:
                    user = User(
                        email=s["email"],
                        full_name=s["full_name"],
                        hashed_password=get_password_hash(s["password"]),
                        is_superuser=s["is_superuser"],
                        is_verified=True,
                        is_active=True,
                    )
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                pr = await session.exec(
                    select(FortuneProfile).where(FortuneProfile.user_id == user.id)
                )
                if not pr.first():
                    session.add(
                        FortuneProfile(
                            user_id=user.id,
                            label="나",
                            solar_date=s["solar_date"],
                            hour=12,
                            minute=0,
                            time_unknown=True,
                            gender=s["gender"],
                        )
                    )
                    await session.commit()
    except Exception as exc:  # pragma: no cover
        print(f"[startup] seed accounts skipped: {exc}")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:6100",
        "http://localhost:6000",  # blocked by Chrome (ERR_UNSAFE_PORT)
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(fortune.router, prefix="/api/fortune", tags=["fortune"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(engagement.router, prefix="/api/engagement", tags=["engagement"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} - Running smoothly"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FortuneOne"}
