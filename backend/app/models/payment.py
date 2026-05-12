from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(unique=True, index=True)
    payment_key: Optional[str] = None
    amount: int
    user_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")
    status: str = Field(default="PENDING") # PENDING, SUCCESS, FAILED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
