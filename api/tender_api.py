from __future__ import annotations
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.auth import get_current_user, require_role
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/tender", tags=["tender"])

WORK_HOURS_PER_DAY = 8


class TenderDocument(BaseModel):
    doc_type: str
    count: int
    hours_per_doc: float


class TenderAssessment(BaseModel):
    tender_name: str
    customer: str
    deadline_date: str
    documents: List[TenderDocument]
    required_disciplines: List[str] = []
    notes: Optional[str] = None


@router.post("/assess")
def assess_tender(
    body: TenderAssessment,
    current_user: User = Depends(get_current_user),
):
    """
    Go/No-Go оценка тендера.
    Анализирует: требуемые ресурсы, текущую загрузку, доступные мощности, вероятность успеха.
    """
    loc = get_locator()
    tasks = loc.planned_task_repo.get_all()
    today = date.today()
    deadline = date.fromisoformat(body.deadline_date)
    calendar_days = (deadline - today).days
    work_days = max(1, sum(1 for d in range(calendar_days + 1)
                           if (today + timedelta(days=d)).weekday() < 5))

    # Требуемые ресурсы для тендера
    total_tender_hours = sum(d.count * d.hours_per_doc for d in body.documents)
    total_tender_docs = sum(d.count for d in body.documents)

    # Текущая загрузка инженеров
    by_eng = {}
    for t in tasks:
        eng = getattr(t, 'engineer', None)
        if not eng:
            continue
        if eng not in by_eng:
            by_eng[eng] = {"remaining_hours": 0, "active_tasks": 0}
        if t.status != "completed":
            ph = getattr(t, 'planned_hours', 0) or 0
            ah = getattr(t, 'actual_hours', 0) or 0
            by_eng[eng]["remaining_hours"] += max(0, ph - ah)
            by_eng[eng]["active_tasks"] += 1

    total_engineers = max(len(by_eng), 1)
    team_capacity = total_engineers * work_days * WORK_HOURS_PER_DAY
    team_remaining_load = sum(e["remaining_hours"] for e in by_eng.values())
    team_free_capacity = max(0, team_capacity - team_remaining_load)

    # Сколько инженеров нужно для тендера
    engineers_needed = max(1, round(total_tender_hours / (work_days * WORK_HOURS_PER_DAY)))
    # Сколько свободных инженеров есть
    available_engineers = sum(
        1 for e in by_eng.values()
        if (e["remaining_hours"] / max(1, work_days * WORK_HOURS_PER_DAY)) < 0.8
    )

    # Оценка рисков
    risks = []
    can_fit = team_free_capacity >= total_tender_hours
    time_sufficient = total_tender_hours / max(1, total_engineers) <= work_days * WORK_HOURS_PER_DAY

    if calendar_days < 14:
        risks.append({"level": "high", "text": f"Критически мало времени: {calendar_days} дней до дедлайна"})
    elif calendar_days < 30:
        risks.append({"level": "medium", "text": f"Ограниченные сроки: {calendar_days} дней до дедлайна"})

    if not can_fit:
        risks.append({"level": "high", "text": f"Не хватает свободных ресурсов: нужно {total_tender_hours:.0f}ч, доступно {team_free_capacity:.0f}ч"})

    if available_engineers < engineers_needed:
        risks.append({"level": "high", "text": f"Не хватает инженеров: нужно {engineers_needed}, доступно {available_engineers}"})

    if team_remaining_load / max(1, team_capacity) > 0.9:
        risks.append({"level": "high", "text": "Команда загружена более чем на 90%"})
    elif team_remaining_load / max(1, team_capacity) > 0.7:
        risks.append({"level": "medium", "text": "Команда загружена более чем на 70%"})

    # Итоговая оценка
    high_risks = sum(1 for r in risks if r["level"] == "high")
    medium_risks = sum(1 for r in risks if r["level"] == "medium")

    if high_risks >= 2:
        decision = "NO_GO"
        decision_label = "Не рекомендуется"
        confidence = "high"
    elif high_risks == 1:
        decision = "RISKY"
        decision_label = "Высокий риск"
        confidence = "medium"
    elif medium_risks >= 2:
        decision = "RISKY"
        decision_label = "Умеренный риск"
        confidence = "medium"
    else:
        decision = "GO"
        decision_label = "Рекомендуется"
        confidence = "high"

    # Прогноз если возьмёмся
    feasibility_pct = min(100, round(team_free_capacity / max(1, total_tender_hours) * 100))

    return {
        "tender": {
            "name": body.tender_name,
            "customer": body.customer,
            "deadline": body.deadline_date,
            "calendar_days": calendar_days,
            "work_days": work_days,
        },
        "requirements": {
            "total_documents": total_tender_docs,
            "total_hours": round(total_tender_hours, 1),
            "engineers_needed": engineers_needed,
            "by_type": [
                {"doc_type": d.doc_type, "count": d.count, "hours": round(d.count * d.hours_per_doc, 1)}
                for d in body.documents
            ],
        },
        "team_capacity": {
            "total_engineers": total_engineers,
            "available_engineers": available_engineers,
            "capacity_hours": round(team_capacity, 1),
            "current_load_hours": round(team_remaining_load, 1),
            "free_hours": round(team_free_capacity, 1),
            "utilization_pct": round(team_remaining_load / max(1, team_capacity) * 100, 1),
        },
        "assessment": {
            "decision": decision,
            "decision_label": decision_label,
            "confidence": confidence,
            "feasibility_pct": feasibility_pct,
            "risks": risks,
        },
    }
