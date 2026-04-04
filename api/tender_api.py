from __future__ import annotations
import math
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from typing import List, Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User
from models.enums import TaskStatus, TaskType

router = APIRouter(prefix="/api/tender", tags=["tender"])

WORK_HOURS_PER_DAY = 8
LOGISTICS_LEVELS = {"low", "normal", "high"}


class TenderDocument(BaseModel):
    doc_type: str
    count: int
    hours_per_doc: float
    discipline: Optional[str] = None


class TenderAssessment(BaseModel):
    tender_name: str
    customer: str
    deadline_date: str
    documents: List[TenderDocument]
    required_disciplines: List[str] = []
    team_size: Optional[int] = None
    expected_review_rounds: int = 1
    expected_remark_count: int = 0
    vdr_required: bool = False
    otk_required: bool = False
    logistics_complexity: str = "normal"
    notes: Optional[str] = None

    @field_validator("expected_review_rounds", "expected_remark_count")
    def non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Значение не может быть отрицательным")
        return value

    @field_validator("logistics_complexity")
    def validate_logistics(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in LOGISTICS_LEVELS:
            raise ValueError(f"Недопустимая сложность логистики: {value}")
        return normalized


def _add_risk(risks: list[dict], level: str, text: str) -> None:
    risks.append({"level": level, "text": text})


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
    calendar_days = max((deadline - today).days, 0)
    work_days = max(1, sum(1 for d in range(calendar_days + 1)
                           if (today + timedelta(days=d)).weekday() < 5))

    # Требуемые ресурсы для тендера
    total_tender_hours = sum(d.count * d.hours_per_doc for d in body.documents)
    total_tender_docs = sum(d.count for d in body.documents)

    # Текущая загрузка инженеров
    by_eng: dict[str, dict[str, float]] = {}
    for t in tasks:
        eng = t.owner_name
        if not eng:
            continue
        if eng not in by_eng:
            by_eng[eng] = {"remaining_hours": 0.0, "active_tasks": 0}
        if t.status != TaskStatus.COMPLETED:
            ph = t.work_hours_planned or 0.0
            ah = t.actual_hours or 0.0
            by_eng[eng]["remaining_hours"] += max(0.0, ph - ah)
            by_eng[eng]["active_tasks"] += 1

    team_size = body.team_size if body.team_size and body.team_size > 0 else len(by_eng)
    total_engineers = max(team_size, 1)
    team_capacity = total_engineers * work_days * WORK_HOURS_PER_DAY
    team_remaining_load = sum(e["remaining_hours"] for e in by_eng.values())
    team_free_capacity = max(0.0, team_capacity - team_remaining_load)

    # Сколько инженеров нужно для тендера
    engineers_needed = max(1, math.ceil(total_tender_hours / max(1, work_days * WORK_HOURS_PER_DAY)))
    # Сколько свободных инженеров есть
    available_engineers = (
        sum(1 for e in by_eng.values()
            if (e["remaining_hours"] / max(1, work_days * WORK_HOURS_PER_DAY)) < 0.8)
        if by_eng else total_engineers
    )

    active_tasks = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED)
    active_review_tasks = sum(
        1 for t in tasks
        if t.status != TaskStatus.COMPLETED and t.task_type in (TaskType.REVIEW, TaskType.APPROVAL)
    )
    blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)

    risks: list[dict] = []
    can_fit = team_free_capacity >= total_tender_hours
    time_sufficient = total_tender_hours <= team_capacity

    if calendar_days < 14:
        _add_risk(risks, "high", f"Критически мало времени: {calendar_days} дней до дедлайна")
    elif calendar_days < 30:
        _add_risk(risks, "medium", f"Ограниченные сроки: {calendar_days} дней до дедлайна")

    if not can_fit:
        _add_risk(risks, "high", f"Не хватает свободных ресурсов: нужно {total_tender_hours:.0f}ч, доступно {team_free_capacity:.0f}ч")

    if available_engineers < engineers_needed:
        _add_risk(risks, "high", f"Не хватает инженеров: нужно {engineers_needed}, доступно {available_engineers}")

    utilization = team_remaining_load / max(1.0, team_capacity)
    if utilization > 0.9:
        _add_risk(risks, "high", "Команда загружена более чем на 90%")
    elif utilization > 0.7:
        _add_risk(risks, "medium", "Команда загружена более чем на 70%")

    if blocked_tasks > 0:
        _add_risk(risks, "medium", f"Есть заблокированные задачи: {blocked_tasks}")

    if total_tender_docs > 150:
        _add_risk(risks, "medium", "Большой объем документации может увеличивать цикл согласования")
    if total_tender_docs > 250:
        _add_risk(risks, "high", "Слишком много документов для быстрого выполнения")

    if body.vdr_required:
        if calendar_days < 35:
            _add_risk(risks, "high", "Требуется VDR и недостаточно времени для его подготовки")
        else:
            _add_risk(risks, "medium", "Подготовка VDR повышает сложность тендера")
        if total_tender_docs > 100:
            _add_risk(risks, "medium", "VDR при большом количестве документов требует дополнительного контроля")

    if body.otk_required:
        if calendar_days < 30:
            _add_risk(risks, "high", "ОТК требуется, а сроки критически короткие")
        elif calendar_days < 45:
            _add_risk(risks, "medium", "Нужна проверка ОТК, время ограничено")

    if body.expected_review_rounds >= 3:
        _add_risk(risks, "high", "Ожидается несколько раундов проверки")
    elif body.expected_review_rounds == 2:
        _add_risk(risks, "medium", "Ожидается дополнительный раунд проверки")

    if body.expected_remark_count > 20:
        _add_risk(risks, "high", "Ожидается много замечаний, требуется дополнительное время на доработку")
    elif body.expected_remark_count > 8:
        _add_risk(risks, "medium", "Ожидается несколько замечаний")

    if body.logistics_complexity == "high":
        if calendar_days < 45:
            _add_risk(risks, "medium", "Высокая логистическая сложность и ограниченные сроки")
        else:
            _add_risk(risks, "medium", "Высокая сложность логистики требует предварительного планирования")

    if active_review_tasks == 0 and body.expected_review_rounds > 1:
        _add_risk(risks, "medium", "Не найдено текущих задач на проверку, проверьте загрузку отдела согласования")

    if body.required_disciplines and total_engineers < len(body.required_disciplines):
        _add_risk(risks, "medium", "Требуется больше дисциплин, чем рассчитано по числу инженеров")

    if not time_sufficient and not body.team_size:
        _add_risk(risks, "medium", "Оценка мощности основана лишь на текущей загрузке, уточните размер команды")

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

    recommendations: list[str] = []
    if not can_fit:
        recommendations.append("Рассмотреть расширение команды или сокращение объема тендера")
    if body.vdr_required:
        recommendations.append("Подготовить VDR и согласовать загруженность по комплекту документов")
    if body.otk_required:
        recommendations.append("Включить в план задачи на ОТК и логистику оборудования")
    if body.expected_review_rounds > 1:
        recommendations.append(f"Планировать {body.expected_review_rounds} раунда проверки")
    if body.expected_remark_count > 0:
        recommendations.append(f"Заложить время на {body.expected_remark_count} ожидаемых замечаний")
    if active_review_tasks > 0:
        recommendations.append("Проверить текущую очередь задач на согласование и корректировку")
    if body.notes:
        recommendations.append("Уточнить дополнительные требования заказчика по примечаниям")

    feasibility_pct = min(100, round(team_free_capacity / max(1, total_tender_hours) * 100))

    return {
        "tender": {
            "name": body.tender_name,
            "customer": body.customer,
            "deadline": body.deadline_date,
            "calendar_days": calendar_days,
            "work_days": work_days,
            "vdr_required": body.vdr_required,
            "otk_required": body.otk_required,
            "logistics_complexity": body.logistics_complexity,
            "required_disciplines": body.required_disciplines,
            "team_size": body.team_size,
        },
        "requirements": {
            "total_documents": total_tender_docs,
            "total_hours": round(total_tender_hours, 1),
            "engineers_needed": engineers_needed,
            "by_type": [
                {
                    "doc_type": d.doc_type,
                    "count": d.count,
                    "hours": round(d.count * d.hours_per_doc, 1),
                    "discipline": d.discipline,
                }
                for d in body.documents
            ],
        },
        "team_capacity": {
            "total_engineers": total_engineers,
            "available_engineers": available_engineers,
            "capacity_hours": round(team_capacity, 1),
            "current_load_hours": round(team_remaining_load, 1),
            "free_hours": round(team_free_capacity, 1),
            "utilization_pct": round(utilization * 100, 1),
            "active_tasks": active_tasks,
            "active_review_tasks": active_review_tasks,
            "blocked_tasks": blocked_tasks,
        },
        "assessment": {
            "decision": decision,
            "decision_label": decision_label,
            "confidence": confidence,
            "feasibility_pct": feasibility_pct,
            "risks": risks,
            "recommendations": recommendations,
        },
    }
