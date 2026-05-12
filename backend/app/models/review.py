from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class CourseReview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    user_id: int = Field(foreign_key="user.id")
    rating: float = Field(default=5.0)
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CourseReviewCreate(SQLModel):
    rating: float = 5.0
    content: str = ""

class CourseReviewRead(SQLModel):
    id: int
    course_id: int
    user_id: int
    rating: float
    content: str
    created_at: datetime
