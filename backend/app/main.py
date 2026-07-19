from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api import auth, fortune, profiles
from app.core.database import engine, async_session_maker
from app.core.security import get_password_hash
from app.models.base import SQLModel
from app.models.user import User
from app.models.fortune_profile import FortuneProfile  # noqa: F401 — create_all
from sqlmodel import select

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    # Create initial admin user if it doesn't exist
    async with async_session_maker() as session:
        result = await session.exec(select(User).where(User.email == "admin@example.com"))
        admin_user = result.first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_verified=True
            )
            session.add(admin_user)
            await session.commit()
            
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

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} - Running smoothly"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FortuneOne"}
