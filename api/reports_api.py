from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import io
from core.auth import require_role
from core.service_locator import get_locator
from models.user import User
from services.report_service import generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/labor")
def export_labor_report(
    project_id: Optional[int] = Query(None, description="Фильтр по проекту"),
    employee_id: Optional[int] = Query(None, description="Фильтр по сотруднику"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin", "manager")),
):
    loc = get_locator()
    # Запрос данных через существующий time_logs + users + projects
    sql = """
        SELECT
            u.full_name                                    AS employee,
            p.name                                         AS project,
            u.discipline                                   AS discipline,
            COALESCE(SUM(pt.work_hours_planned), 0)        AS planned_hours,
            COALESCE(SUM(tl.hours), 0)                     AS actual_hours,
            CASE WHEN SUM(pt.work_hours_planned) > 0
                 THEN ROUND(SUM(tl.hours)::numeric /
                      SUM(pt.work_hours_planned) * 100, 1)
                 ELSE 0 END                                AS pct_done,
            0                                              AS rate,
            0                                              AS planned_cost,
            0                                              AS actual_cost,
            0                                              AS delta,
            0                                              AS overhead,
            0                                              AS total_cost,
            0                                              AS profitability
        FROM time_logs tl
        JOIN users u ON u.id = tl.user_id
        JOIN projects p ON p.id = tl.project_id
        LEFT JOIN planned_tasks pt ON pt.assigned_to = tl.user_id
            AND pt.project_id = tl.project_id
        WHERE TRUE
    """
    params: list = []
    if project_id:
        sql += " AND tl.project_id = %s"
        params.append(project_id)
    if employee_id:
        sql += " AND tl.user_id = %s"
        params.append(employee_id)
    if date_from:
        sql += " AND tl.day >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND tl.day <= %s"
        params.append(date_to)
    sql += " GROUP BY u.full_name, p.name, u.discipline ORDER BY p.name, u.full_name"

    rows = loc.db.fetch_all(sql, tuple(params)) if params else loc.db.fetch_all(sql)
    keys = ["employee", "project", "discipline", "planned_hours", "actual_hours",
            "pct_done", "rate", "planned_cost", "actual_cost", "delta",
            "overhead", "total_cost", "profitability"]
    data = [dict(zip(keys, row)) for row in rows]

    xlsx = generate_excel_report("labor", data, "Трудозатраты_ч-ч")
    filename = f"labor_report{'_p'+str(project_id) if project_id else ''}.xlsx"
    return StreamingResponse(
        io.BytesIO(xlsx),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )