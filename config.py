from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass
class Config:
    """
    Конфигурация ДокПоток IRIS.

    Варианты использования:
    - Config()           — берёт всё из env или дефолтов.
    - Config(db_dsn=..., storage_root=...) — явные параметры.
    """

    db_dsn: str
    storage_root: str

    def __init__(
        self,
        db_dsn: str | None = None,
        storage_root: str | None = None,
    ) -> None:
        # DSN к Postgres: env → явный параметр → дефолт
        self.db_dsn = db_dsn or os.getenv(
            "IRIS_DB_DSN",
            # Поменяй на свои креды, если нужно:
            "postgresql://postgres:Qwerty852@localhost:5432/iris",
        )

        # Каталог для файлов (загруженные документы, отчёты)
        default_storage = os.path.join(os.path.dirname(__file__), "storage")
        self.storage_root = storage_root or os.getenv(
            "IRIS_STORAGE_ROOT",
            default_storage,
        )

        os.makedirs(self.storage_root, exist_ok=True)


def load_config() -> Config:
    return Config(
        db_dsn=os.getenv(
            "DB_DSN", "postgresql://dms_user:dms_pass@localhost:5432/dms"
        ),
        storage_root=os.getenv("STORAGE_ROOT", "./data/docs"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
