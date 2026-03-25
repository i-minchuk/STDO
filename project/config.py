# from dataclasses import dataclass
# import os


# @dataclass
# class Config:
#     db_dsn: str
#     storage_root: str


# def load_config() -> Config:
#     return Config(
#         db_dsn=os.getenv("DB_DSN", "postgresql://user:pass@localhost:5432/dms"),
#         storage_root=os.getenv("STORAGE_ROOT", "./data/docs"),
#     )

# config.py
from dataclasses import dataclass
import os


@dataclass
class Config:
    db_dsn: str
    storage_root: str


def load_config() -> Config:
    return Config(
        db_dsn=os.getenv("DB_DSN", "postgresql://dms_user:dms_pass@localhost:5432/dms"),
        storage_root=os.getenv("STORAGE_ROOT", "./data/docs"),
    )
# postgresql://dms_user:dms_pass@db:5432/dms