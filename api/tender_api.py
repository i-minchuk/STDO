from __future__ import annotations
import math
import logging
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from core.auth import get_current_user, require_role
from core.service_locator import get_locator
from models.user import User
from models.enums import TaskStatus, TaskType

router = APIRouter(prefix="/api/tender", tags=["tender"])

logger = logging.getLogger(__name__)

WORK_HOURS_PER_DAY = 8
LOGISTICS_LEVELS = {"low", "normal", "high"}


class TenderDocument(BaseModel):
    doc_type: str
    count: int
    hours_per_doc: float
    discipline: Optional[str] = None

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Количество документов должно быть больше 0")
        return v

    @field_validator("hours_per_doc")
    @classmethod
    def validate_hours(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Часов на документ должно быть больше 0")
        return v


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
    save_tender: bool = False  # New: whether to save tender to DB

    @field_validator("expected_review_rounds", "expected_remark_count")
    @classmethod
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

    @model_validator(mode="after")
    def validate_documents_not_empty(self) -> TenderAssessment:
        if not self.documents:
            raise ValueError("Список документов не может быть пустым")
        return self

    @model_validator(mode="after")
    def validate_deadline(self) -> TenderAssessment:
        try:
            deadline = date.fromisoformat(self.deadline_date)
            if deadline < date.today():
                raise ValueError("Дата дедлайна не может быть в прошлом")
        except ValueError as e:
            if "deadline" in str(e).lower():
                raise
            raise ValueError("Некорректный формат даты дедлайна")
        return self

    @model_validator(mode="after")
    def validate_team_size(self) -> TenderAssessment:
        if self.team_size is not None and self.team_size <= 0:
            raise ValueError("Размер команды должен быть больше 0")
        return self


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
    try:
        loc = get_locator()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис не инициализирован",
        )

    try:
        tasks = loc.planned_task_repo.get_all()
    except Exception as e:
        logger.exception("Error loading tasks")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке задач: {str(e)}",
        )

    today = date.today()

    # Validate deadline date format
    try:
        deadline = date.fromisoformat(body.deadline_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат даты. Используйте формат YYYY-MM-DD",
        )

    # Additional deadline check (in case model_validator was bypassed)
    if deadline < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата дедлайна не может быть в прошлом",
        )

    calendar_days = max((deadline - today).days, 0)

    # Use work schedule from DB if available
    try:
        schedule = loc.work_schedule_repo.get_default_schedule()
        if schedule:
            work_days = loc.work_schedule_repo.count_work_days(today, deadline, schedule)
        else:
            # Fallback: simple Mon-Fri calculation
            work_days = max(1, sum(1 for d in range(calendar_days + 1)
                                   if (today + timedelta(days=d)).weekday() < 5))
    except Exception:
        # Fallback to simple calculation if DB query fails
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

    # Determine team size - use user input or calculate from available engineers
    team_size = body.team_size if body.team_size and body.team_size > 0 else max(len(by_eng), 1)
    total_engineers = max(team_size, 1)

    # Prevent division by zero
    work_hours_capacity = max(1, work_days) * WORK_HOURS_PER_DAY
    team_capacity = total_engineers * work_hours_capacity
    team_remaining_load = sum(e["remaining_hours"] for e in by_eng.values())
    team_free_capacity = max(0.0, team_capacity - team_remaining_load)

    # Сколько инженеров нужно для тендера
    engineers_needed = max(1, math.ceil(total_tender_hours / work_hours_capacity))
    # Сколько свободных инженеров есть
    available_engineers = (
        sum(1 for e in by_eng.values()
            if (e["remaining_hours"] / work_hours_capacity) < 0.8)
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

    assessment_result = {
        "decision": decision,
        "decision_label": decision_label,
        "confidence": confidence,
        "feasibility_pct": feasibility_pct,
        "risks": risks,
        "recommendations": recommendations,
    }

    # Save tender to DB if requested
    tender_id = None
    if body.save_tender:
        try:
            with loc.db.transaction():  # Wrap in transaction
                tender = loc.tender_repo.insert(
                    name=body.tender_name,
                    customer=body.customer,
                    deadline_date=deadline,
                    vdr_required=body.vdr_required,
                    otk_required=body.otk_required,
                    logistics_complexity=body.logistics_complexity,
                    notes=body.notes,
                    required_disciplines=body.required_disciplines,
                    team_size=body.team_size,
                    expected_review_rounds=body.expected_review_rounds,
                    expected_remark_count=body.expected_remark_count,
                    created_by=current_user.id,
                )
                # Add documents
                for doc in body.documents:
                    loc.tender_repo.add_document(
                        tender_id=tender.id,
                        doc_type=doc.doc_type,
                        count=doc.count,
                        hours_per_doc=doc.hours_per_doc,
                        discipline=doc.discipline,
                    )
                # Update status to assessed
                loc.tender_repo.update_status(tender.id, "assessed", assessment_result)
                tender_id = tender.id
        except Exception as e:
            logger.exception("Failed to save tender")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не удалось сохранить тендер: {str(e)}",
            )

    return {
        "tender": {
            "id": tender_id,
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
        "assessment": assessment_result,
    }


# New endpoints for CRUD operations

@router.get("/")
def list_tenders(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
    """List all tenders with optional status filter."""
    loc = get_locator()
    
    # Get total count for pagination
    if status:
        count_row = loc.tender_repo._db.fetch_one(
            "SELECT COUNT(*) as cnt FROM tenders WHERE status = %s",
            (status,)
        )
        tenders = loc.tender_repo.get_by_status(status, limit, offset)
    else:
        count_row = loc.tender_repo._db.fetch_one("SELECT COUNT(*) as cnt FROM tenders")
        tenders = loc.tender_repo.get_all(limit, offset)

    total = count_row["cnt"] if count_row else 0

    return {
        "tenders": [
            {
                "id": t.id,
                "name": t.name,
                "customer": t.customer,
                "deadline_date": str(t.deadline_date),
                "status": t.status,
                "created_at": str(t.created_at) if t.created_at else None,
                "assessed_at": str(t.assessed_at) if t.assessed_at else None,
            }
            for t in tenders
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{tender_id}")
def get_tender(
    tender_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get tender details by ID."""
    loc = get_locator()
    tender = loc.tender_repo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тендер #{tender_id} не найден",
        )

    documents = loc.tender_repo.get_documents(tender_id)

    return {
        "id": tender.id,
        "name": tender.name,
        "customer": tender.customer,
        "deadline_date": str(tender.deadline_date),
        "status": tender.status,
        "vdr_required": tender.vdr_required,
        "otk_required": tender.otk_required,
        "logistics_complexity": tender.logistics_complexity,
        "notes": tender.notes,
        "required_disciplines": tender.required_disciplines,
        "team_size": tender.team_size,
        "expected_review_rounds": tender.expected_review_rounds,
        "expected_remark_count": tender.expected_remark_count,
        "created_by": tender.created_by,
        "created_at": str(tender.created_at) if tender.created_at else None,
        "assessed_at": str(tender.assessed_at) if tender.assessed_at else None,
        "assessment_result": tender.assessment_result,
        "documents": [
            {
                "id": d.id,
                "doc_type": d.doc_type,
                "count": d.count,
                "hours_per_doc": d.hours_per_doc,
                "discipline": d.discipline,
            }
            for d in documents
        ],
    }


@router.delete("/{tender_id}")
def delete_tender(
    tender_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
):
    """Delete a tender."""
    loc = get_locator()
    tender = loc.tender_repo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тендер #{tender_id} не найден",
        )

    success = loc.tender_repo.delete(tender_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить тендер",
        )

    return {"message": f"Тендер #{tender_id} удалён"}


@router.post("/{tender_id}/status")
def update_tender_status(
    tender_id: int,
    status: str,
    current_user: User = Depends(require_role("admin", "manager")),
):
    """Update tender status."""
    valid_statuses = ["draft", "assessed", "approved", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}",
        )

    loc = get_locator()
    tender = loc.tender_repo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тендер #{tender_id} не найден",
        )

    # Preserve assessment_result when transitioning to approved/rejected
    assessment_result = tender.assessment_result
    if status in ("approved", "rejected") and tender.assessment_result:
        assessment_result = dict(tender.assessment_result)
        assessment_result["status_changed_at"] = datetime.now().isoformat()
        assessment_result["status_changed_by"] = current_user.id

    updated = loc.tender_repo.update_status(tender_id, status, assessment_result)
    return {
        "id": updated.id,
        "status": updated.status,
    }
