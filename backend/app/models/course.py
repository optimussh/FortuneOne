from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

# ─── Course ──────────────────────────────────────────────────
class CourseBase(SQLModel):
    title: str
    description: Optional[str] = None
    price: int = Field(default=0)  # 0 = 무료
    thumbnail_url: Optional[str] = None
    is_published: bool = Field(default=False)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    level: str = ""  # 입문, 초급, 중급, 고급
    tags: Optional[str] = None  # comma-separated
    rating_avg: float = Field(default=0.0)
    review_count: int = Field(default=0)

class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instructor_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    instructor: "User" = Relationship(back_populates="courses")
    modules: List["Module"] = Relationship(
        back_populates="course", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    enrollments: List["Enrollment"] = Relationship(back_populates="course")

class CourseCreate(SQLModel):
    title: str
    description: Optional[str] = None
    price: int = 0
    thumbnail_url: Optional[str] = None
    category_id: Optional[int] = None
    level: str = ""
    tags: Optional[str] = None

class CourseRead(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime

class CourseReadWithDetail(CourseRead):
    modules: List["ModuleRead"] = []
    enrollment_count: Optional[int] = None

# ─── Module ──────────────────────────────────────────────────
class ModuleBase(SQLModel):
    title: str
    order_index: int = Field(default=0)

class Module(ModuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id")

    course: Course = Relationship(back_populates="modules")
    lessons: List["Lesson"] = Relationship(
        back_populates="module", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ModuleCreate(SQLModel):
    title: str
    order_index: int = 0

class ModuleRead(ModuleBase):
    id: int
    course_id: int
    lessons: List["LessonRead"] = []

# ─── Lesson ──────────────────────────────────────────────────
class LessonBase(SQLModel):
    title: str
    content_type: str = Field(default="video")  # "video" | "text"
    video_source_type: Optional[str] = None  # "LINK" | "UPLOAD"
    content_url: Optional[str] = None
    text_content: Optional[str] = None
    order_index: int = Field(default=0)

class Lesson(LessonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="module.id")

    module: Module = Relationship(back_populates="lessons")

class LessonCreate(SQLModel):
    title: str
    content_type: str = "video"
    video_source_type: Optional[str] = None
    content_url: Optional[str] = None
    text_content: Optional[str] = None
    order_index: int = 0

class LessonRead(LessonBase):
    id: int
    module_id: int

# ─── Enrollment ──────────────────────────────────────────────
class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)

    course: Course = Relationship(back_populates="enrollments")
    user: "User" = Relationship(back_populates="enrollments")

class EnrollmentRead(SQLModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
