Модули: замечания, геймификация (расширенная), VDR/MDR, загрузка файлов, отчёты

-- ─── 1. ХРАНИЛИЩЕ ЗАГРУЖЕННЫХ ФАЙЛОВ ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS uploaded_files (
    id           SERIAL PRIMARY KEY,
    file_id      UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    original_name TEXT NOT NULL,
    stored_path  TEXT NOT NULL,
    size_bytes   BIGINT NOT NULL,
    mime_type    TEXT NOT NULL,
    uploaded_by  INTEGER REFERENCES users(id),
    uploaded_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_uploaded_files_file_id ON uploaded_files(file_id);

-- ─── 2. РАСШИРЕНИЕ document_revisions: привязка к uploaded_files ────────────
-- Если колонки нет — добавляем
ALTER TABLE document_revisions
    ADD COLUMN IF NOT EXISTS uploaded_file_id INTEGER REFERENCES uploaded_files(id),
    ADD COLUMN IF NOT EXISTS validation_profile TEXT DEFAULT 'ESKD',
    ADD COLUMN IF NOT EXISTS validation_passed BOOLEAN,
    ADD COLUMN IF NOT EXISTS validation_errors JSONB DEFAULT '[]'::jsonb;

-- ─── 3. ЗАМЕЧАНИЯ ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS remarks (
    id                 SERIAL PRIMARY KEY,
    project_id         INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    document_id        INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    revision_id        INTEGER REFERENCES document_revisions(id) ON DELETE SET NULL,
    author_id          INTEGER REFERENCES users(id),
    assignee_id        INTEGER REFERENCES users(id),
    source             TEXT NOT NULL DEFAULT 'internal',  -- internal / customer / reviewer
    text               TEXT NOT NULL,
    status             TEXT NOT NULL DEFAULT 'open',
    -- open / resolved / rejected / superseded
    resolution_comment TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at        TIMESTAMPTZ
);
CREATE INDEX idx_remarks_project ON remarks(project_id);
CREATE INDEX idx_remarks_status  ON remarks(project_id, status);

-- ─── 4. ОТВЕТЫ НА ЗАМЕЧАНИЯ ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS remark_responses (
    id          SERIAL PRIMARY KEY,
    remark_id   INTEGER NOT NULL REFERENCES remarks(id) ON DELETE CASCADE,
    author_id   INTEGER NOT NULL REFERENCES users(id),
    text        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_remark_responses_remark ON remark_responses(remark_id);

-- ─── 5. VDR (Vendor Document Register) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS vdr_entries (
    id                     SERIAL PRIMARY KEY,
    project_id             INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    doc_number             TEXT NOT NULL,
    title                  TEXT NOT NULL,
    discipline             TEXT,
    responsible_contractor TEXT,
    latest_revision        TEXT,
    latest_upload_date     TIMESTAMPTZ,
    status                 TEXT,
    is_auto_filled         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_vdr_project_docnum ON vdr_entries(project_id, doc_number);

-- ─── 6. MDR (Master Document Register) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS mdr_entries (
    id                 SERIAL PRIMARY KEY,
    project_id         INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    doc_number         TEXT NOT NULL,
    title              TEXT NOT NULL,
    discipline         TEXT,
    revision_current   TEXT,
    planned_issue_date DATE,
    actual_issue_date  DATE,
    status             TEXT,
    is_auto_filled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX uq_mdr_project_docnum ON mdr_entries(project_id, doc_number);

-- ─── 7. РАСШИРЕНИЕ геймификации (score events) ───────────────────────────────
ALTER TABLE gamification_events
    ADD COLUMN IF NOT EXISTS action_key  TEXT,
    ADD COLUMN IF NOT EXISTS ref_doc_id  INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS ref_task_id INTEGER REFERENCES planned_tasks(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS comment     TEXT;
