from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional
from datetime import datetime
import httpx

from app.core.database import get_session
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.payment import Payment
from app.models.course import Enrollment
from pydantic import BaseModel

router = APIRouter()


class PaymentConfirmRequest(BaseModel):
    payment_key: str
    order_id: str
    amount: int
    course_id: int


@router.post("/confirm")
async def confirm_payment(
    body: PaymentConfirmRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """토스페이먼츠 결제 승인 및 수강 등록"""

    # 1) 토스페이먼츠 승인 API 호출
    toss_secret = settings.TOSS_SECRET_KEY
    if not toss_secret:
        raise HTTPException(status_code=500, detail="결제 설정이 완료되지 않았습니다")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            json={
                "paymentKey": body.payment_key,
                "orderId": body.order_id,
                "amount": body.amount,
            },
            headers={
                "Authorization": f"Basic {toss_secret}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code != 200:
        # 승인 실패
        payment = Payment(
            order_id=body.order_id,
            payment_key=body.payment_key,
            amount=body.amount,
            user_id=current_user.id,
            course_id=body.course_id,
            status="FAILED",
        )
        session.add(payment)
        await session.commit()
        raise HTTPException(status_code=400, detail="결제 승인에 실패했습니다")

    # 2) 결제 성공 → DB 저장
    payment = Payment(
        order_id=body.order_id,
        payment_key=body.payment_key,
        amount=body.amount,
        user_id=current_user.id,
        course_id=body.course_id,
        status="SUCCESS",
        approved_at=datetime.utcnow(),
    )
    session.add(payment)

    # 3) 자동 수강 등록
    existing = await session.exec(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == body.course_id,
        )
    )
    if not existing.first():
        enrollment = Enrollment(user_id=current_user.id, course_id=body.course_id)
        session.add(enrollment)

    await session.commit()
    return {"status": "SUCCESS", "message": "결제가 완료되었습니다"}
