from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

# ─── Follow ──────────────────────────────────────────────────
class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="user.id", index=True)
    following_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FollowRead(SQLModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime
