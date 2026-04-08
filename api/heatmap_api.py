from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/heatmap", tags=["heatmap"])


@router.get("/weekly")
def weekly_heatmap(
    user_id: Optional[int] = Query(None, description="ID пользователя. По умолчанию — текущий пользователь"),
    weeks: int = Query(12, description="Количество недель для отображения (макс. 52)"),
    current_user: User = Depends(get_current_user),
):
    """Получить недельную тепловую карту активности пользователя."""
    loc = get_locator()
    
    target_user_id = user_id if user_id else current_user.id
    
    # Ограничиваем количество недель
    weeks = max(1, min(weeks, 52))
    
    heatmap_data = loc.heatmap_service.generate_weekly_heatmap(target_user_id, weeks)
    
    return {
        "user_id": target_user_id,
        "weeks": weeks,
        "heatmap": heatmap_data,
    }


@router.get("/monthly")
def monthly_heatmap(
    user_id: Optional[int] = Query(None, description="ID пользователя. По умолчанию — текущий пользователь"),
    months: int = Query(12, description="Количество месяцев для отображения (макс. 24)"),
    current_user: User = Depends(get_current_user),
):
    """Получить месячную тепловую карту активности пользователя."""
    loc = get_locator()
    
    target_user_id = user_id if user_id else current_user.id
    
    # Ограничиваем количество месяцев
    months = max(1, min(months, 24))
    
    heatmap_data = loc.heatmap_service.generate_monthly_heatmap(target_user_id, months)
    
    return {
        "user_id": target_user_id,
        "months": months,
        "heatmap": heatmap_data,
    }


@router.get("/summary")
def activity_summary(
    user_id: Optional[int] = Query(None, description="ID пользователя. По умолчанию — текущий пользователь"),
    days: int = Query(30, description="Количество дней для анализа (макс. 90)"),
    current_user: User = Depends(get_current_user),
):
    """Получить сводку активности пользователя за последние N дней."""
    loc = get_locator()
    
    target_user_id = user_id if user_id else current_user.id
    
    # Ограничиваем количество дней
    days = max(1, min(days, 90))
    
    summary = loc.heatmap_service.get_user_activity_summary(target_user_id, days)
    
    return {
        "user_id": target_user_id,
        "days": days,
        "summary": summary,
    }