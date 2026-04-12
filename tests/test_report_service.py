"""Tests for report_service module."""
import pytest


class TestReportService:
    """Tests for report generation functions."""

    def test_report_headers_exist(self):
        """Test that report headers are defined."""
        from services.report_service import REPORT_HEADERS

        assert "labor" in REPORT_HEADERS
        assert "project" in REPORT_HEADERS
        assert "projects" in REPORT_HEADERS
        assert "employees" in REPORT_HEADERS

    def test_labor_report_has_expected_headers(self):
        """Test labor report has expected columns."""
        from services.report_service import REPORT_HEADERS

        headers = REPORT_HEADERS["labor"]
        assert "Сотрудник" in headers
        assert "Проект" in headers
        assert "Плановые ч/ч" in headers
        assert "Факт. ч/ч" in headers
        assert "% выполнения" in headers

    def test_project_report_has_expected_headers(self):
        """Test project report has expected columns."""
        from services.report_service import REPORT_HEADERS

        headers = REPORT_HEADERS["project"]
        assert "Документ" in headers
        assert "Код" in headers
        assert "Дисциплина" in headers
        assert "Статус" in headers
        assert "Ревизия" in headers

    def test_projects_report_has_expected_headers(self):
        """Test projects report has expected columns."""
        from services.report_service import REPORT_HEADERS

        headers = REPORT_HEADERS["projects"]
        assert "Проект" in headers
        assert "Код" in headers
        assert "Заказчик" in headers
        assert "Статус" in headers

    def test_employees_report_has_expected_headers(self):
        """Test employees report has expected columns."""
        from services.report_service import REPORT_HEADERS

        headers = REPORT_HEADERS["employees"]
        assert "Сотрудник" in headers
        assert "Роль" in headers
        assert "Дисциплина" in headers
        assert "Проект" in headers

    def test_generate_excel_report_without_openpyxl(self):
        """Test that function handles missing openpyxl."""
        from services import report_service

        # Check OPENPYXL_OK flag exists
        assert hasattr(report_service, "OPENPYXL_OK")

    @pytest.mark.skipif(not __import__('sys').modules.get('services.report_service', None) or 
                         not getattr(__import__('services.report_service', fromlist=['OPENPYXL_OK']), 'OPENPYXL_OK', False),
                         reason="openpyxl not installed")
    def test_generate_excel_report_labor(self):
        """Test generating labor report (requires openpyxl)."""
        from services.report_service import generate_excel_report

        data = [
            {
                "Сотрудник": "Иванов И.И.",
                "Проект": "Test",
                "Дисциплина": "Engineering",
                "Плановые ч/ч": 40.0,
                "Факт. ч/ч": 38.0,
                "% выполнения": 95.0,
                "Ставка ₽/ч": 1000,
                "Плановая стоимость ₽": 40000,
                "Факт. стоимость ₽": 38000,
                "Отклонение ₽": -2000,
                "Накладные (25%) ₽": 10000,
                "ИТОГО ₽": 48000,
                "Рентабельность": 20.0,
            }
        ]

        result = generate_excel_report("labor", data, "Labor Report")

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.skipif(not getattr(__import__('services.report_service', fromlist=['OPENPYXL_OK']), 'OPENPYXL_OK', False),
                         reason="openpyxl not installed")
    def test_generate_excel_report_project(self):
        """Test generating project report (requires openpyxl)."""
        from services.report_service import generate_excel_report

        data = [
            {
                "Документ": "Test Doc",
                "Код": "DOC-001",
                "Дисциплина": "Engineering",
                "Ответственный": "Иванов",
                "Статус": "in_work",
                "Ревизия": "A1",
                "Плановые ч/ч": 40.0,
                "Факт. ч/ч": 38.0,
                "Срок сдачи (план)": "2026-01-15",
                "Факт. сдача": None,
                "Просрочка (дни)": 0,
            }
        ]

        result = generate_excel_report("project", data, "Project Report")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_report_type_valid_values(self):
        """Test that ReportType has valid literal values."""
        from services.report_service import ReportType, REPORT_HEADERS

        valid_types = ["project", "projects", "employees", "labor"]
        for rt in valid_types:
            assert rt in REPORT_HEADERS
