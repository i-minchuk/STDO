from fastapi import APIRouter, Depends
from core.service_locator import ServiceLocator, get_locator

router = APIRouter(tags=["internal-projects"])


@router.post("/projects/{project_id}/recalc_cpm_and_metrics")
def recalc_cpm_and_metrics(
    project_id: int,
    locator: ServiceLocator = Depends(get_locator),
):
    critical = locator.cpm_scheduler.recalculate_project_schedule(project_id)
    locator.project_dashboard.recalculate_project_metrics(project_id)
    return {"status": "ok", "critical_tasks_count": len(critical)}