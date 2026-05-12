from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, col
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..core.database import get_session
from ..api.deps import get_current_user
from ..models.user import User
from ..models.mentor import (
    MentorProfile, MentorProfileCreate,
    MentoringRequest, MentoringRequestCreate,
    MentoringReview, MentoringReviewCreate,
)

router = APIRouter(prefix="/api/mentoring", tags=["mentoring"])

# ─── 멘토 목록 ───────────────────────────────────────────────
@router.get("/mentors")
async def list_mentors(
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(MentorProfile).where(MentorProfile.is_active == True)
    if q:
        stmt = stmt.where(col(MentorProfile.bio).icontains(q))
    if category:
        stmt = stmt.where(col(MentorProfile.tags).icontains(category))
    stmt = stmt.order_by(MentorProfile.mentee_count.desc()).offset(offset).limit(limit)
    result = await session.exec(stmt)
    mentors = result.all()

    # Enrich with user info
    enriched = []
    for m in mentors:
        user = await session.get(User, m.user_id)
        enriched.append({
            **m.model_dump(),
            "nickname": user.nickname if user else "",
            "handle": user.handle if user else "",
            "avatar_url": user.avatar_url if user else None,
        })
    return enriched


# ─── 멘토 상세 ───────────────────────────────────────────────
@router.get("/mentors/{mentor_id}")
async def get_mentor(mentor_id: int, session: AsyncSession = Depends(get_session)):
    mentor = await session.get(MentorProfile, mentor_id)
    if not mentor:
        raise HTTPException(404, "멘토를 찾을 수 없습니다")
    user = await session.get(User, mentor.user_id)

    # Fetch reviews
    result = await session.exec(
        select(MentoringReview)
        .where(MentoringReview.mentor_profile_id == mentor_id)
        .order_by(MentoringReview.created_at.desc())
        .limit(50)
    )
    reviews = result.all()
    reviews_enriched = []
    for r in reviews:
        reviewer = await session.get(User, r.reviewer_id)
        reviews_enriched.append({
            **r.model_dump(),
            "reviewer_nickname": reviewer.nickname if reviewer else "익명",
        })

    return {
        **mentor.model_dump(),
        "nickname": user.nickname if user else "",
        "handle": user.handle if user else "",
        "avatar_url": user.avatar_url if user else None,
        "full_name": user.full_name if user else "",
        "reviews": reviews_enriched,
    }


# ─── 멘토 등록 ───────────────────────────────────────────────
@router.post("/mentors/register")
async def register_mentor(
    data: MentorProfileCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    existing = await session.exec(
        select(MentorProfile).where(MentorProfile.user_id == user.id)
    )
    if existing.first():
        raise HTTPException(400, "이미 멘토로 등록되어 있습니다")

    mentor = MentorProfile(user_id=user.id, **data.model_dump())
    session.add(mentor)
    await session.commit()
    await session.refresh(mentor)
    return mentor


# ─── 멘토링 신청 ─────────────────────────────────────────────
@router.post("/requests")
async def create_mentoring_request(
    data: MentoringRequestCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    mentor = await session.get(MentorProfile, data.mentor_profile_id)
    if not mentor:
        raise HTTPException(404, "멘토를 찾을 수 없습니다")
    if mentor.user_id == user.id:
        raise HTTPException(400, "본인에게 멘토링 신청할 수 없습니다")

    req = MentoringRequest(
        mentor_profile_id=data.mentor_profile_id,
        mentee_id=user.id,
        price=mentor.hourly_price,
        message=data.message,
        scheduled_at=data.scheduled_at,
    )
    session.add(req)

    # Update mentee count
    mentor.mentee_count += 1
    session.add(mentor)

    await session.commit()
    await session.refresh(req)
    return req


# ─── 내 멘토링 요청 목록 (멘토용) ────────────────────────────
@router.get("/requests/received")
async def list_received_requests(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    mentor = (await session.exec(
        select(MentorProfile).where(MentorProfile.user_id == user.id)
    )).first()
    if not mentor:
        raise HTTPException(404, "멘토 프로필이 없습니다")

    result = await session.exec(
        select(MentoringRequest)
        .where(MentoringRequest.mentor_profile_id == mentor.id)
        .order_by(MentoringRequest.created_at.desc())
    )
    requests = result.all()
    enriched = []
    for r in requests:
        mentee = await session.get(User, r.mentee_id)
        enriched.append({
            **r.model_dump(),
            "mentee_nickname": mentee.nickname if mentee else "익명",
            "mentee_email": mentee.email if mentee else "",
        })
    return enriched


# ─── 멘토링 상태 변경 ────────────────────────────────────────
@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    status: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    req = await session.get(MentoringRequest, request_id)
    if not req:
        raise HTTPException(404, "요청을 찾을 수 없습니다")

    mentor = await session.get(MentorProfile, req.mentor_profile_id)
    if not mentor or mentor.user_id != user.id:
        raise HTTPException(403, "권한이 없습니다")

    req.status = status
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return req


# ─── 멘토링 리뷰 작성 ────────────────────────────────────────
@router.post("/reviews")
async def create_mentoring_review(
    data: MentoringReviewCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    mentor = await session.get(MentorProfile, data.mentor_profile_id)
    if not mentor:
        raise HTTPException(404, "멘토를 찾을 수 없습니다")

    review = MentoringReview(
        mentor_profile_id=data.mentor_profile_id,
        reviewer_id=user.id,
        rating=data.rating,
        content=data.content,
    )
    session.add(review)

    # Update mentor stats
    mentor.review_count += 1
    total = mentor.rating_avg * (mentor.review_count - 1) + data.rating
    mentor.rating_avg = round(total / mentor.review_count, 1)
    session.add(mentor)

    await session.commit()
    await session.refresh(review)
    return review
