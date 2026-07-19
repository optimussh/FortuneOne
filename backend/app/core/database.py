from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

# Default SQLite file lives next to backend package root: backend/data/fortuneone.db
_url = settings.DATABASE_URL
_connect_args: dict = {}
_engine_kwargs: dict = {"echo": False, "future": True}

if _url.startswith("sqlite"):
    # ensure parent dir for file-based sqlite
    if ":///" in _url:
        raw_path = _url.split(":///", 1)[1]
        # strip query string
        raw_path = raw_path.split("?", 1)[0]
        if raw_path and raw_path != ":memory:":
            db_path = Path(raw_path)
            if not db_path.is_absolute():
                # resolve relative to backend/ (cwd when running uvicorn from backend/)
                db_path = Path.cwd() / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(_url, connect_args=_connect_args, **_engine_kwargs)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with async_session_maker() as session:
        yield session
