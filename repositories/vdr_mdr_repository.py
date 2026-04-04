from __future__ import annotations
from typing import List, Optional
from models.vdr_mdr import VDREntry, MDREntry
from datetime import datetime, timezone


class VDRRepository:
    def __init__(self, db):
        self._db = db

    def upsert(self, project_id: int, doc_number: str, title: str,
               discipline: Optional[str], contractor: Optional[str],
               revision: Optional[str], upload_date: datetime,
               status: Optional[str]) -> VDREntry:
        row = self._db.fetch_one(
            """INSERT INTO vdr_entries
               (project_id, doc_number, title, discipline, responsible_contractor,
                latest_revision, latest_upload_date, status, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now())
               ON CONFLICT (project_id, doc_number) DO UPDATE SET
                   latest_revision = EXCLUDED.latest_revision,
                   latest_upload_date = EXCLUDED.latest_upload_date,
                   status = EXCLUDED.status,
                   updated_at = now()
               RETURNING id, project_id, doc_number, title, discipline,
               responsible_contractor, latest_revision, latest_upload_date,
               status, is_auto_filled, updated_at""",
            (project_id, doc_number, title, discipline, contractor,
             revision, upload_date, status),
        )
        return VDREntry.from_row(row)

    def get_by_project(self, project_id: int) -> List[VDREntry]:
        rows = self._db.fetch_all(
            """SELECT id, project_id, doc_number, title, discipline,
               responsible_contractor, latest_revision, latest_upload_date,
               status, is_auto_filled, updated_at
               FROM vdr_entries WHERE project_id=%s ORDER BY doc_number""",
            (project_id,),
        )
        return [VDREntry.from_row(r) for r in rows]

    def get_by_project_paginated(self, project_id: int, limit: int = 20, offset: int = 0) -> tuple[List[VDREntry], int]:
        """Get VDR entries for project with pagination.

        Returns:
            Tuple of (entries list, total count)
        """
        rows = self._db.fetch_all(
            """SELECT id, project_id, doc_number, title, discipline,
               responsible_contractor, latest_revision, latest_upload_date,
               status, is_auto_filled, updated_at
               FROM vdr_entries WHERE project_id=%s ORDER BY doc_number
               LIMIT %s OFFSET %s""",
            (project_id, limit, offset),
        )
        entries = [VDREntry.from_row(r) for r in rows]

        # Get total count
        total_row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM vdr_entries WHERE project_id=%s",
            (project_id,),
        )
        total = int(total_row["cnt"]) if total_row else 0

        return entries, total


class MDRRepository:
    def __init__(self, db):
        self._db = db

    def upsert(self, project_id: int, doc_number: str, title: str,
               discipline: Optional[str], revision: Optional[str],
               status: Optional[str]) -> MDREntry:
        row = self._db.fetch_one(
            """INSERT INTO mdr_entries
               (project_id, doc_number, title, discipline, revision_current, status, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,now())
               ON CONFLICT (project_id, doc_number) DO UPDATE SET
                   revision_current = EXCLUDED.revision_current,
                   status = EXCLUDED.status,
                   updated_at = now()
               RETURNING id, project_id, doc_number, title, discipline,
               revision_current, planned_issue_date, actual_issue_date,
               status, is_auto_filled, updated_at""",
            (project_id, doc_number, title, discipline, revision, status),
        )
        return MDREntry.from_row(row)

    def get_by_project(self, project_id: int) -> List[MDREntry]:
        rows = self._db.fetch_all(
            """SELECT id, project_id, doc_number, title, discipline,
               revision_current, planned_issue_date, actual_issue_date,
               status, is_auto_filled, updated_at
               FROM mdr_entries WHERE project_id=%s ORDER BY doc_number""",
            (project_id,),
        )
        return [MDREntry.from_row(r) for r in rows]

    def get_by_project_paginated(self, project_id: int, limit: int = 20, offset: int = 0) -> tuple[List[MDREntry], int]:
        """Get MDR entries for project with pagination.

        Returns:
            Tuple of (entries list, total count)
        """
        rows = self._db.fetch_all(
            """SELECT id, project_id, doc_number, title, discipline,
               revision_current, planned_issue_date, actual_issue_date,
               status, is_auto_filled, updated_at
               FROM mdr_entries WHERE project_id=%s ORDER BY doc_number
               LIMIT %s OFFSET %s""",
            (project_id, limit, offset),
        )
        entries = [MDREntry.from_row(r) for r in rows]

        # Get total count
        total_row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM mdr_entries WHERE project_id=%s",
            (project_id,),
        )
        total = int(total_row["cnt"]) if total_row else 0

        return entries, total