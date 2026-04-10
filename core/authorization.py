"""
Утилиты для проверки прав доступа к проектам и документам.
"""
from fastapi import HTTPException
from core.service_locator import get_locator
from models.user import User


def check_project_access(project_id: int, user: User) -> None:
    """
    Проверить доступ пользователя к проекту.
    
    Текущая логика: все аутентифицированные пользователи имеют доступ.
    В будущем можно добавить проверку membership в проекте.
    
    Raises:
        HTTPException 404: если проект не найден
    """
    loc = get_locator()
    project = loc.project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")


def check_document_access(document_id: int, user: User) -> None:
    """
    Проверить доступ пользователя к документу.
    
    Проверяет существование документа и проекта.
    
    Raises:
        HTTPException 404: если документ или проект не найден
    """
    loc = get_locator()
    doc = loc.document_repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    project = loc.project_repo.get_by_id(doc.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект документа не найден")


def check_task_access(task_id: int, user: User) -> None:
    """
    Проверить доступ пользователя к задаче.
    
    Проверяет существование задачи и связанного проекта.
    
    Raises:
        HTTPException 404: если задача или проект не найден
    """
    loc = get_locator()
    task = loc.planned_task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    project = loc.project_repo.get_by_id(task.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект задачи не найден")
