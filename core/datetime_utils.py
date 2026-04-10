"""Утилиты для работы с datetime с учётом временных зон.

Используем UTC для всех timestamps в БД и API.
"""
from datetime import datetime, timezone

# UTC timezone-aware datetime
def utc_now() -> datetime:
    """Вернуть текущее время в UTC с timezone."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Вернуть текущее время в UTC в ISO формате."""
    return utc_now().isoformat()


def datetime_to_utc(dt: datetime) -> datetime:
    """Конвертировать datetime в UTC timezone-aware.
    
    Если datetime уже с timezone - просто возвращаем.
    Если naive datetime (без timezone) - считаем что это UTC.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    # naive datetime - считаем что это UTC
    return dt.replace(tzinfo=timezone.utc)


def parse_iso_date(date_str: str) -> datetime:
    """Парсить ISO строку в datetime с UTC timezone."""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return datetime_to_utc(dt)


def format_iso(dt: datetime) -> str:
    """Форматировать datetime в ISO строку для JSON."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# Alias для обратной совместимости
now_utc = utc_now
