from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal
import re

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from models.enums import ValidationProfile

ValidationSeverity = Literal["CRITICAL", "WARNING"]


@dataclass
class ValidationError:
    rule: str
    severity: ValidationSeverity
    message: str
    page: int | None = None


@dataclass
class ValidationResult:
    passed: bool
    profile: str
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "profile": self.profile,
            "errors": [{"rule": e.rule, "message": e.message, "page": e.page}
                       for e in self.errors],
            "warnings": [{"rule": w.rule, "message": w.message, "page": w.page}
                         for w in self.warnings],
        }


class BaseChecker(ABC):
    @abstractmethod
    def check(self, doc, meta: dict) -> list[ValidationError]:
        ...


class TitleBlockChecker(BaseChecker):
    """ЕСКД ГОСТ 2.104-2006: обязательные поля основной надписи"""
    REQUIRED_FIELDS = ["Разраб.", "Пров.", "Н. контр.", "Утв.", "Лист", "Листов"]

    def check(self, doc, meta: dict) -> list[ValidationError]:
        if not PYMUPDF_AVAILABLE:
            return []
        errors = []
        last_page = doc[-1]
        text = last_page.get_text()
        for fname in self.REQUIRED_FIELDS:
            if fname not in text:
                errors.append(ValidationError(
                    rule="ESKD_2.104_TITLEBLOCK",
                    severity="CRITICAL",
                    message=f"Поле «{fname}» отсутствует в основной надписи",
                    page=len(doc),
                ))
        return errors


class DateFormatChecker(BaseChecker):
    """Дата должна быть в формате ДД.ММ.ГГГГ"""
    WRONG = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')

    def check(self, doc, meta: dict) -> list[ValidationError]:
        if not PYMUPDF_AVAILABLE:
            return []
        errors = []
        for i, page in enumerate(doc):
            if self.WRONG.search(page.get_text()):
                errors.append(ValidationError(
                    rule="DATE_FORMAT_ISO",
                    severity="WARNING",
                    message="Обнаружена дата в формате ISO (ГГГГ-ММ-ДД). Требуется ДД.ММ.ГГГГ",
                    page=i + 1,
                ))
        return errors


class DrawingFrameChecker(BaseChecker):
    """Проверка наличия рамки чертежа"""
    def check(self, doc, meta: dict) -> list[ValidationError]:
        if not PYMUPDF_AVAILABLE:
            return []
        errors = []
        for i, page in enumerate(doc):
            paths = page.get_drawings()
            has_frame = any(
                p.get("type") == "re" and p.get("rect") and p["rect"].width > 150
                for p in paths
            )
            if not has_frame:
                errors.append(ValidationError(
                    rule="DRAWING_FRAME_MISSING",
                    severity="CRITICAL",
                    message="Рамка чертежа отсутствует или некорректна",
                    page=i + 1,
                ))
        return errors


class EmptySignatureChecker(BaseChecker):
    """Проверка незаполненных полей подписей"""
    def check(self, doc, meta: dict) -> list[ValidationError]:
        if not PYMUPDF_AVAILABLE:
            return []
        errors = []
        for page in doc:
            for widget in (page.widgets() or []):
                name_lower = (widget.field_name or "").lower()
                if any(k in name_lower for k in ("подп", "sign", "signature")):
                    if not widget.field_value:
                        errors.append(ValidationError(
                            rule="SIGNATURE_EMPTY",
                            severity="CRITICAL",
                            message=f"Подпись «{widget.field_name}» не заполнена",
                            page=page.number + 1,
                        ))
        return errors


# Профили: какие чекеры включены
PROFILE_CHECKERS: dict[str, list[BaseChecker]] = {
    ValidationProfile.ESKD: [
        TitleBlockChecker(), DateFormatChecker(),
        DrawingFrameChecker(), EmptySignatureChecker(),
    ],
    ValidationProfile.GOST_R: [
        TitleBlockChecker(), DateFormatChecker(), EmptySignatureChecker(),
    ],
    ValidationProfile.CUSTOMER_GAZPROM: [
        TitleBlockChecker(), EmptySignatureChecker(),
    ],
    ValidationProfile.CUSTOMER_ROSATOM: [
        TitleBlockChecker(), DrawingFrameChecker(), EmptySignatureChecker(),
    ],
}


def validate_document_file(file_path: str, profile: str, meta: dict) -> ValidationResult:
    checkers = PROFILE_CHECKERS.get(profile, PROFILE_CHECKERS[ValidationProfile.ESKD])
    all_errors: list[ValidationError] = []

    if PYMUPDF_AVAILABLE and file_path.lower().endswith(".pdf"):
        import fitz
        doc = fitz.open(file_path)
        for checker in checkers:
            all_errors.extend(checker.check(doc, meta))
        doc.close()

    criticals = [e for e in all_errors if e.severity == "CRITICAL"]
    warnings = [e for e in all_errors if e.severity == "WARNING"]

    return ValidationResult(
        passed=len(criticals) == 0,
        profile=profile,
        errors=criticals,
        warnings=warnings,
    )