from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

# ─── MentorProfile ───────────────────────────────────────────
class MentorProfileBase(SQLModel):
    job_title: str = ""
    career_level: str = ""  # "주니어 (1~3년)", "미들 (4~8년)", "시니어 (9년 이상)", "Lead 레벨"
    company: str = ""
    bio: str = ""  # 마크다운 지원
    hourly_price: int = 0
    session_minutes: int = 60
    max_per_session: int = 1
    tags: Optional[str] = None  # comma-separated
    is_active: bool = True

class MentorProfile(MentorProfileBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    rating_avg: float = Field(default=0.0)
    review_count: int = Field(default=0)
    mentee_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="mentor_profile")
    requests: List["MentoringRequest"] = Relationship(back_populates="mentor_profile")
    reviews: List["MentoringReview"] = Relationship(back_populates="mentor_profile")

class MentorProfileCreate(SQLModel):
    job_title: str
    career_level: str = ""
    company: str = ""
    bio: str = ""
    hourly_price: int = 0
    session_minutes: int = 60
    tags: Optional[str] = None

class MentorProfileRead(MentorProfileBase):
    id: int
    user_id: int
    rating_avg: float
    review_count: int
    mentee_count: int
    # will be enriched with user info in API

# ─── MentoringRequest ────────────────────────────────────────
class MentoringRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_profile_id: int = Field(foreign_key="mentorprofile.id")
    mentee_id: int = Field(foreign_key="user.id")
    status: str = Field(default="PENDING")  # PENDING, ACCEPTED, COMPLETED, CANCELLED
    message: str = ""
    price: int = 0
    scheduled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    mentor_profile: MentorProfile = Relationship(back_populates="requests")

class MentoringRequestCreate(SQLModel):
    mentor_profile_id: int
    message: str = ""
    scheduled_at: Optional[datetime] = None

# ─── MentoringReview ─────────────────────────────────────────
class MentoringReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mentor_profile_id: int = Field(foreign_key="mentorprofile.id")
    reviewer_id: int = Field(foreign_key="user.id")
    rating: float = Field(default=5.0)
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    mentor_profile: MentorProfile = Relationship(back_populates="reviews")

class MentoringReviewCreate(SQLModel):
    mentor_profile_id: int
    rating: float = 5.0
    content: str = ""

class MentoringReviewRead(SQLModel):
    id: int
    mentor_profile_id: int
    reviewer_id: int
    rating: float
    content: str
    created_at: datetime
