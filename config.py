import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    db_dsn: str
    storage_root: str
    log_level: str = "INFO"
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


def load_config() -> Config:
    return Config(
        db_dsn=os.getenv(
            "DB_DSN", "postgresql://dms_user:dms_pass@localhost:5432/dms"
        ),
        storage_root=os.getenv("STORAGE_ROOT", "./data/docs"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
