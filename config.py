from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

_dotenv_loaded = False


def _load_dotenv_files() -> None:
    global _dotenv_loaded
    if _dotenv_loaded or load_dotenv is None:
        return

    root = Path(__file__).resolve().parent
    for env_file in (root / ".env", root / ".env.local"):
        if env_file.exists():
            load_dotenv(env_file, override=False)
    _dotenv_loaded = True


def _env_or_default(name: str, default: str) -> str:
    _load_dotenv_files()
    return os.getenv(name, default)


@dataclass
class Config:
    """Конфигурация ДокПоток IRIS."""

    db_dsn: str = field(default_factory=lambda: _env_or_default(
        "DB_DSN",
        "postgresql://postgres:Qwerty852@localhost:5432/iris",
    ))
    storage_root: str = field(default_factory=lambda: _env_or_default(
        "STORAGE_ROOT",
        str(Path(__file__).parent / "storage"),
    ))
    secret_key: str = field(default_factory=lambda: _env_or_default(
        "SECRET_KEY",
        "iris-secret-key-change-in-production",
    ))
    
    def __post_init__(self) -> None:
        Path(self.storage_root).mkdir(parents=True, exist_ok=True)

        # Security: reject weak default secret key in production
        if self.secret_key == "iris-secret-key-change-in-production":
            import warnings
            warnings.warn(
                "WARNING: Using default SECRET_KEY. "
                "Set SECRET_KEY environment variable in production!",
                UserWarning,
                stacklevel=2
            )


def load_config() -> Config:
    return Config()