from api.gamification_api import award_gamification_with_badges
from dto.common import ProjectShortDTO
from dto.portfolio_today import PortfolioTodayOverviewDTO
from dto.pagination import PaginatedResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectFromTenderRequest(BaseModel):
    tender_name: str
    customer: str
    deadline_date: str
    documents: List[dict]  # [{"doc_type": str, "count": int, "hours_per_doc": float, "discipline": str}]
    team_size: Optional[int] = None
    vdr_required: bool = False
    otk_required: bool = False
    logistics_complexity: str = "normal"
    custom_fields: Optional[Dict[str, Any]] = None  # Гибкие поля для заказчика


@router.post("/create-from-tender")
def create_project_from_tender(
    body: CreateProjectFromTenderRequest,
    current_user: User = Depends(get_current_user),
    locator: ServiceLocator = Depends(get_locator),
):
    """
    Создать проект из тендера.
    Автоматически планирует задачи для VDR, CRS, OTK, логистики.
    """
    # Генерируем код проекта
    today = date.today()
    year = today.year
    existing_codes = [p.code for p in locator.project_repo.list_all() if p.code.startswith(f"PRJ-{year}")]
    next_num = len(existing_codes) + 1
    project_code = f"PRJ-{year}-{next_num:03d}"

    # Создаём проект
    project = locator.project_repo.insert(
        code=project_code,
        name=body.tender_name,
        customer=body.customer,
        status=ProjectStatus.PLANNED,
        manager_id=current_user.id,
        start_date=today,
        end_date_planned=date.fromisoformat(body.deadline_date),
        custom_fields=body.custom_fields,
        vdr_required=body.vdr_required,
        otk_required=body.otk_required,
        crs_deadline_days=3,  # Фиксировано по требованиям
        logistics_delivery_weeks=2,  # Фиксировано по требованиям
        logistics_complexity=body.logistics_complexity,
    )

    # Планируем задачи
    tasks_created = _plan_project_tasks(locator, project, body)

    # Начисляем геймификацию за принятие тендера
    _award_gamification(locator, current_user.id, "tender_accepted", points=50, project_id=project.id, comment=f"Принят тендер: {body.tender_name}")

    return {
        "project": {
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "status": project.status.value,
        },
        "tasks_created": tasks_created,
        "message": "Проект создан из тендера. Задачи запланированы.",
    }


def _plan_project_tasks(locator: ServiceLocator, project, body: CreateProjectFromTenderRequest) -> int:
    """Планирует задачи для проекта на основе тендера."""
    tasks = []
    start_date = project.start_date
    deadline = project.end_date_planned

    # Задачи по документам
    for doc in body.documents:
        doc_type = doc["doc_type"]
        count = doc["count"]
        hours_per_doc = doc["hours_per_doc"]
        discipline = doc.get("discipline", doc_type)

        # Задача на разработку документа
        tasks.append({
            "name": f"Разработка {doc_type} ({count} шт.)",
            "task_type": TaskType.ENGINEERING,
            "duration_days": max(1, int(count * hours_per_doc / 8)),  # Предполагаем 8ч/день
            "work_hours": count * hours_per_doc,
            "discipline": discipline,
        })

        # Задача на проверку
        tasks.append({
            "name": f"Проверка {doc_type}",
            "task_type": TaskType.REVIEW,
            "duration_days": 2,
            "work_hours": 16,  # 2 дня по 8ч
            "discipline": discipline,
        })

    # VDR задачи
    if body.vdr_required:
        tasks.append({
            "name": "Подготовка VDR",
            "task_type": TaskType.ENGINEERING,
            "duration_days": 10,
            "work_hours": 80,
            "discipline": "Документация",
        })
        tasks.append({
            "name": "Проверка VDR",
            "task_type": TaskType.REVIEW,
            "duration_days": 3,
            "work_hours": 24,
            "discipline": "Документация",
        })

    # OTK задачи
    if body.otk_required:
        tasks.append({
            "name": "Подготовка к ОТК",
            "task_type": TaskType.ENGINEERING,
            "duration_days": 5,
            "work_hours": 40,
            "discipline": "Качество",
        })
        tasks.append({
            "name": "Проведение ОТК",
            "task_type": TaskType.APPROVAL,
            "duration_days": 2,
            "work_hours": 16,
            "discipline": "Качество",
        })

    # Логистика
    if body.logistics_complexity in ["normal", "high"]:
        logistics_days = 14 if body.logistics_complexity == "normal" else 21
        tasks.append({
            "name": f"Организация логистики ({body.logistics_complexity})",
            "task_type": TaskType.OTHER,
            "duration_days": logistics_days // 7,  # В неделях
            "work_hours": logistics_days * 4,  # Предполагаем 4ч/день
            "discipline": "Логистика",
        })

    # Создаём задачи в БД
    task_count = 0
    current_start = start_date
    for task_data in tasks:
        end_date = current_start + timedelta(days=task_data["duration_days"] - 1)
        locator.planned_task_repo.insert(
            project_id=project.id,
            project_code=project.code,
            project_name=project.name,
            document_id=None,
            document_code=None,
            revision_id=None,
            revision_index=None,
            name=task_data["name"],
            task_type=task_data["task_type"],
            assigned_to=None,  # Назначить позже
            owner_name=None,
            duration_days_planned=task_data["duration_days"],
            work_hours_planned=task_data["work_hours"],
            start_date_planned=current_start,
            end_date_planned=end_date,
            status=TaskStatus.NOT_STARTED,
        )
        task_count += 1
        current_start = end_date + timedelta(days=1)  # Следующая задача на следующий день

    # Пересчитываем CPM
    locator.cpm_scheduler.recalculate_project_schedule(project.id)
    locator.project_dashboard.recalculate_project_metrics(project.id)

    return task_count


def _award_gamification(locator: ServiceLocator, user_id: int, event_type: str, points: int, project_id: Optional[int] = None, comment: Optional[str] = None):
    """Начисляет очки геймификации."""
    award_gamification_with_badges(
        locator=locator,
        user_id=user_id,
        event_type=event_type,
        points=points,
        project_id=project_id,
        comment=comment,
    )


@router.get("/", response_model=PaginatedResponse[ProjectShortDTO])
def list_projects(
    limit: int = Query(20, gt=0, le=1000),
    offset: int = Query(0, ge=0),
    locator: ServiceLocator = Depends(get_locator)
):
    """List projects with pagination support."""
    projects, total = locator.project_repo.list_all_paginated(limit=limit, offset=offset)
    items = [
        ProjectShortDTO(
            id=p.id, code=p.code, name=p.name, status=p.status.value,
        )
        for p in projects
    ]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/portfolio/today", response_model=PortfolioTodayOverviewDTO)
def get_portfolio_today(locator: ServiceLocator = Depends(get_locator)):
    today = date.today()
    return locator.project_dashboard.get_portfolio_today_overview_dto(today)
