from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

# ─── Clip ────────────────────────────────────────────────────
class ClipBase(SQLModel):
    title: str
    content: str = ""  # 마크다운
    category: str = ""  # "기술", "홍보", "자유", "팁"
    tags: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

class Clip(ClipBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    like_count: int = Field(default=0)
    view_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    comments: List["ClipComment"] = Relationship(back_populates="clip")
    likes: List["ClipLike"] = Relationship(back_populates="clip")

class ClipCreate(SQLModel):
    title: str
    content: str = ""
    category: str = ""
    tags: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

class ClipRead(ClipBase):
    id: int
    author_id: int
    like_count: int
    view_count: int
    comment_count: int
    created_at: datetime

# ─── ClipComment ─────────────────────────────────────────────
class ClipComment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    clip_id: int = Field(foreign_key="clip.id")
    author_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    clip: Clip = Relationship(back_populates="comments")

class ClipCommentCreate(SQLModel):
    content: str

class ClipCommentRead(SQLModel):
    id: int
    clip_id: int
    author_id: int
    content: str
    created_at: datetime

# ─── ClipLike ────────────────────────────────────────────────
class ClipLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    clip_id: int = Field(foreign_key="clip.id")
    user_id: int = Field(foreign_key="user.id")

    clip: Clip = Relationship(back_populates="likes")
