from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col
from sqlalchemy.orm import selectinload
from typing import List
import os, uuid, shutil

from app.core.database import get_session
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.course import (
    Course, CourseCreate, CourseRead, CourseReadWithDetail,
    Module, ModuleCreate, ModuleRead,
    Lesson, LessonCreate, LessonRead,
    Enrollment, EnrollmentRead,
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Course CRUD ─────────────────────────────────────────────

@router.get("/", response_model=List[CourseRead])
async def list_courses(
    skip: int = 0,
    limit: int = 20,
    q: str = "",
    session: AsyncSession = Depends(get_session),
):
    """공개된 강의 목록 (검색 지원)"""
    stmt = select(Course).where(Course.is_published == True)
    if q:
        stmt = stmt.where(col(Course.title).contains(q))
    stmt = stmt.offset(skip).limit(limit).order_by(Course.created_at.desc())
    result = await session.exec(stmt)
    return result.all()


@router.get("/{course_id}", response_model=CourseReadWithDetail)
async def get_course(course_id: int, session: AsyncSession = Depends(get_session)):
    """강의 상세 (모듈+레슨 포함)"""
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.modules).selectinload(Module.lessons),  # type: ignore
            selectinload(Course.enrollments),  # type: ignore
        )
    )
    result = await session.exec(stmt)
    course = result.first()
    if not course:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다")
    # attach enrollment count
    course_dict = CourseReadWithDetail.model_validate(course)
    course_dict.enrollment_count = len(course.enrollments)
    return course_dict


@router.post("/", response_model=CourseRead, status_code=201)
async def create_course(
    body: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """새 강의 생성 (로그인 필요)"""
    course = Course(**body.model_dump(), instructor_id=current_user.id)
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    body: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    for key, val in body.model_dump().items():
        setattr(course, key, val)
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


@router.patch("/{course_id}/publish", response_model=CourseRead)
async def toggle_publish(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    course.is_published = not course.is_published
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


# ─── My courses (instructor) ────────────────────────────────

@router.get("/instructor/my", response_model=List[CourseRead])
async def my_courses(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(Course).where(Course.instructor_id == current_user.id).order_by(Course.created_at.desc())
    )
    return result.all()


# ─── Module CRUD ─────────────────────────────────────────────

@router.post("/{course_id}/modules", response_model=ModuleRead, status_code=201)
async def add_module(
    course_id: int,
    body: ModuleCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    module = Module(**body.model_dump(), course_id=course_id)
    session.add(module)
    await session.commit()
    await session.refresh(module)
    return ModuleRead.model_validate(module)


# ─── Lesson CRUD ─────────────────────────────────────────────

@router.post("/{course_id}/modules/{module_id}/lessons", response_model=LessonRead, status_code=201)
async def add_lesson(
    course_id: int,
    module_id: int,
    body: LessonCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    lesson = Lesson(**body.model_dump(), module_id=module_id)
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return lesson


@router.post("/{course_id}/modules/{module_id}/lessons/upload", response_model=LessonRead, status_code=201)
async def upload_lesson_video(
    course_id: int,
    module_id: int,
    title: str,
    order_index: int = 0,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """비디오 파일 직접 업로드"""
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    # Save file
    ext = os.path.splitext(file.filename or "video.mp4")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    lesson = Lesson(
        title=title,
        content_type="video",
        video_source_type="UPLOAD",
        content_url=f"/uploads/{filename}",
        module_id=module_id,
        order_index=order_index,
    )
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return lesson


# ─── Enrollment ──────────────────────────────────────────────

@router.post("/{course_id}/enroll", response_model=EnrollmentRead, status_code=201)
async def enroll(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    # 이미 수강 중인지 확인
    existing = await session.exec(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id,
        )
    )
    if existing.first():
        raise HTTPException(status_code=400, detail="이미 수강 중인 강의입니다")

    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


@router.get("/enrolled/my", response_model=List[CourseRead])
async def my_enrolled_courses(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """내가 수강 중인 강의 목록"""
    result = await session.exec(
        select(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.user_id == current_user.id)
    )
    return result.all()
