from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

# ─── Roadmap ─────────────────────────────────────────────────
class RoadmapBase(SQLModel):
    title: str
    description: str = ""
    thumbnail_url: Optional[str] = None
    is_published: bool = False

class Roadmap(RoadmapBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    steps: List["RoadmapStep"] = Relationship(back_populates="roadmap")

class RoadmapCreate(SQLModel):
    title: str
    description: str = ""
    thumbnail_url: Optional[str] = None

class RoadmapRead(RoadmapBase):
    id: int
    creator_id: int
    created_at: datetime

class RoadmapReadWithSteps(RoadmapRead):
    steps: List["RoadmapStepRead"] = []

# ─── RoadmapStep ─────────────────────────────────────────────
class RoadmapStep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roadmap_id: int = Field(foreign_key="roadmap.id")
    course_id: int = Field(foreign_key="course.id")
    step_order: int = Field(default=0)
    description: str = ""

    roadmap: Roadmap = Relationship(back_populates="steps")

class RoadmapStepCreate(SQLModel):
    course_id: int
    step_order: int = 0
    description: str = ""

class RoadmapStepRead(SQLModel):
    id: int
    roadmap_id: int
    course_id: int
    step_order: int
    description: str
