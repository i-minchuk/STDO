from typing import Any, Generic, Optional, Sequence, Type, TypeVar, Protocol
from db.database import Database

T = TypeVar("T")


class ModelProtocol(Protocol):
    id: int


class BaseRepository(Generic[T]):
    """Base class for all repositories to reduce boilerplate."""

    def __init__(self, db: Database, model_class: Type[T], table_name: str, columns: str) -> None:
        self._db = db
        self._model_class = model_class
        self._table_name = table_name
        self._columns = columns

    def get_by_id(self, entity_id: int) -> Optional[T]:
        row = self._db.fetch_one(
            f"SELECT {self._columns} FROM {self._table_name} WHERE id = %s",
            (entity_id,),
        )
        return self._row_to_model(row) if row else None

    def list_all(self, order_by: str = "id") -> Sequence[T]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} ORDER BY {order_by}"
        )
        return [self._row_to_model(r) for r in rows]

    def delete(self, entity_id: int) -> bool:
        result = self._db.execute(
            f"DELETE FROM {self._table_name} WHERE id = %s",
            (entity_id,),
        )
        return result > 0

    def _row_to_model(self, row: dict) -> T:
        """Convert a database row (dict) to a model instance.
        
        By default, it uses keyword arguments to the model class constructor.
        If the model requires special handling (e.g. JSON fields, Enums), 
        subclasses should override this.
        """
        return self._model_class(**row)

    def _get_paginated(
        self, 
        where_sql: str = "", 
        params: tuple[Any, ...] = (), 
        order_by: str = "id", 
        limit: int = 20, 
        offset: int = 0
    ) -> tuple[Sequence[T], int]:
        """Generic helper for paginated queries."""
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name}{where_sql} "
            f"ORDER BY {order_by} LIMIT %s OFFSET %s",
            (*params, limit, offset),
        )
        items = [self._row_to_model(r) for r in rows]

        total_row = self._db.fetch_one(
            f"SELECT count(*) AS cnt FROM {self._table_name}{where_sql}",
            params,
        )
        total = int(total_row["cnt"]) if total_row else 0

        return items, total
