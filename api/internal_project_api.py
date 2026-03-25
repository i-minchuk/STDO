from fastapi import APIRouter, Depends, HTTPException

from core.service_locator import ServiceLocator, get_locator

router = APIRouter(tags=["internal-projects"])


@router.post("/projects/{project_id}/recalc_cpm_and_metrics")
def recalc_cpm_and_metrics(
    project_id: int,
    locator: ServiceLocator = Depends(get_locator),
):
    project = locator.project_repo.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    critical = locator.cpm_scheduler.recalculate_project_schedule(project_id)
    locator.project_dashboard.recalculate_project_metrics(project_id)
    return {"status": "ok", "critical_tasks_count": len(critical)}
