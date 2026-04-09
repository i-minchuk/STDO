from __future__ import annotations
from typing import Optional, Sequence
import json
from datetime import datetime, date

from db.database import Database
from models.tender import Tender, TenderDocument


class TenderRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, name, customer, deadline_date, status,
        vdr_required, otk_required, logistics_complexity, notes,
        required_disciplines, team_size, expected_review_rounds, expected_remark_count,
        created_by, created_at, assessed_at, assessment_result
    """

    def get_by_id(self, tender_id: int) -> Optional[Tender]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM tenders WHERE id = %s",
            (tender_id,),
        )
        return self._row_to_model(row) if row else None

    def get_all(self, limit: int = 50, offset: int = 0) -> Sequence[Tender]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM tenders ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_status(self, status: str, limit: int = 50, offset: int = 0) -> Sequence[Tender]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM tenders WHERE status = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (status, limit, offset),
        )
        return [self._row_to_model(r) for r in rows]

    def get_filtered(
        self,
        status: Optional[str] = None,
        customer: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[Tender], int]:
        """Get filtered tenders with pagination and total count."""
        conditions = []
        params = []
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        if customer:
            conditions.append("customer ILIKE %s")
            params.append(f"%{customer}%")
        if date_from:
            conditions.append("deadline_date >= %s")
            params.append(date_from)
        if date_to:
            conditions.append("deadline_date <= %s")
            params.append(date_to)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        # Get total count
        count_row = self._db.fetch_one(
            f"SELECT COUNT(*) as cnt FROM tenders {where_clause}",
            tuple(params),
        )
        total = count_row["cnt"] if count_row else 0
        
        # Get filtered results
        query = f"""
            SELECT {self._COLUMNS} FROM tenders
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        rows = self._db.fetch_all(query, tuple(params))
        
        return [self._row_to_model(r) for r in rows], total

    def insert(
        self,
        name: str,
        customer: str,
        deadline_date: date,
        vdr_required: bool = False,
        otk_required: bool = False,
        logistics_complexity: str = "normal",
        notes: Optional[str] = None,
        required_disciplines: list[str] = None,
        team_size: Optional[int] = None,
        expected_review_rounds: int = 1,
        expected_remark_count: int = 0,
        created_by: Optional[int] = None,
    ) -> Tender:
        # Fix: json.dumps only if not None
        disciplines_json = json.dumps(required_disciplines) if required_disciplines else None
        
        row = self._db.fetch_one(
            f"""
            INSERT INTO tenders (
                name, customer, deadline_date, status,
                vdr_required, otk_required, logistics_complexity, notes,
                required_disciplines, team_size, expected_review_rounds, expected_remark_count,
                created_by
            ) VALUES (%s, %s, %s, 'draft', %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (
                name, customer, deadline_date,
                vdr_required, otk_required, logistics_complexity, notes,
                disciplines_json,
                team_size, expected_review_rounds, expected_remark_count,
                created_by,
            ),
        )
        return self._row_to_model(row)

    def update_status(
        self,
        tender_id: int,
        status: str,
        assessment_result: Optional[dict] = None,
    ) -> Optional[Tender]:
        assessed_at = datetime.now() if status == "assessed" else None
        self._db.execute(
            """
            UPDATE tenders
            SET status = %s, assessed_at = COALESCE(%s, assessed_at), assessment_result = %s
            WHERE id = %s
            """,
            (status, assessed_at, json.dumps(assessment_result) if assessment_result else None, tender_id),
        )
        return self.get_by_id(tender_id)

    def delete(self, tender_id: int) -> bool:
        result = self._db.execute("DELETE FROM tenders WHERE id = %s", (tender_id,))
        return result > 0

    # TenderDocument methods
    def get_documents(self, tender_id: int) -> Sequence[TenderDocument]:
        rows = self._db.fetch_all(
            "SELECT id, tender_id, doc_type, count, hours_per_doc, discipline FROM tender_documents WHERE tender_id = %s ORDER BY id",
            (tender_id,),
        )
        return [TenderDocument.from_row(r) for r in rows]

    def add_document(
        self,
        tender_id: int,
        doc_type: str,
        count: int,
        hours_per_doc: float,
        discipline: Optional[str] = None,
    ) -> TenderDocument:
        row = self._db.fetch_one(
            """
            INSERT INTO tender_documents (tender_id, doc_type, count, hours_per_doc, discipline)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, tender_id, doc_type, count, hours_per_doc, discipline
            """,
            (tender_id, doc_type, count, hours_per_doc, discipline),
        )
        return TenderDocument.from_row(row)

    def add_documents_batch(
        self,
        tender_id: int,
        documents: list[dict],
    ) -> Sequence[TenderDocument]:
        created = []
        for doc in documents:
            created.append(self.add_document(
                tender_id=tender_id,
                doc_type=doc["doc_type"],
                count=doc["count"],
                hours_per_doc=doc["hours_per_doc"],
                discipline=doc.get("discipline"),
            ))
        return created

    def delete_document(self, document_id: int) -> bool:
        result = self._db.execute("DELETE FROM tender_documents WHERE id = %s", (document_id,))
        return result > 0

    @staticmethod
    def _row_to_model(row: dict) -> Tender:
        # Fix: guard against None row
        if row is None:
            return None
        if row.get("required_disciplines"):
            if isinstance(row["required_disciplines"], str):
                row["required_disciplines"] = json.loads(row["required_disciplines"])
        if row.get("assessment_result") and isinstance(row["assessment_result"], str):
            row["assessment_result"] = json.loads(row["assessment_result"])
        return Tender.from_row(row)
