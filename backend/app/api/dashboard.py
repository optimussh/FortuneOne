from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/metrics")
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    # Mock data for dashboard
    return {
        "kpis": {
            "total_users": {"value": "12,847", "change": "+12%"},
            "monthly_revenue": {"value": "$184,320", "change": "+8%"},
            "active_subscriptions": {"value": "3,291", "change": "-3%"},
            "conversion_rate": {"value": "4.8%", "change": "+0.6%"}
        },
        "revenue_chart": [
            {"name": "Jan", "total": 1200},
            {"name": "Feb", "total": 2100},
            {"name": "Mar", "total": 3400},
            {"name": "Apr", "total": 3100},
            {"name": "May", "total": 4500},
            {"name": "Jun", "total": 5200},
        ],
        "users_chart": [
            {"name": "Week 1", "active": 400, "new": 240},
            {"name": "Week 2", "active": 300, "new": 139},
            {"name": "Week 3", "active": 200, "new": 980},
            {"name": "Week 4", "active": 278, "new": 390},
        ]
    }
