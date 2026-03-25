-- CREATE TABLE documents (
--     id SERIAL PRIMARY KEY,
--     project_id INTEGER NOT NULL REFERENCES projects (id),
--     code TEXT NOT NULL,
--     title TEXT NOT NULL,
--     discipline TEXT,
--     status TEXT NOT NULL, -- enum-like: in_work/on_review/approved/archived
--     current_revision_id INTEGER NULL,
--     created_by INTEGER NOT NULL REFERENCES users (id),
--     created_at TIMESTAMPTZ NOT NULL DEFAULT now()
-- );

-- CREATE TABLE document_revisions (
--     id SERIAL PRIMARY KEY,
--     document_id INTEGER NOT NULL REFERENCES documents (id),
--     revision_index TEXT NOT NULL,
--     version_number INTEGER NOT NULL,
--     status TEXT NOT NULL, -- draft/on_review/approved/superseded
--     file_path TEXT NOT NULL,
--     change_log TEXT,
--     created_by INTEGER NOT NULL REFERENCES users (id),
--     created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
--     approved_by INTEGER NULL REFERENCES users (id),
--     approved_at TIMESTAMPTZ NULL
-- );

-- -- быстрая выборка текущей версии документа
-- ALTER TABLE documents
--     ADD CONSTRAINT fk_documents_current_revision
--     FOREIGN KEY (current_revision_id) REFERENCES document_revisions (id);

-- CREATE UNIQUE INDEX uq_document_revision_version
--     ON document_revisions (document_id, version_number);

-- CREATE INDEX idx_document_revisions_document
--     ON document_revisions (document_id);

-- 000_initial.sql
-- Базовая схема для проектов, документов, ревизий, задач, зависимостей и учёта времени.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Пользователи (упрощённо, можно интегрировать с корпоративной AD/LDAP)
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    login           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'engineer',  -- engineer, manager, admin
    discipline      TEXT,
    rank            TEXT NOT NULL DEFAULT 'junior',    -- junior/middle/senior/lead
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- Проекты
CREATE TABLE projects (
    id                      SERIAL PRIMARY KEY,
    code                    TEXT NOT NULL UNIQUE,
    name                    TEXT NOT NULL,
    customer                TEXT,
    status                  TEXT NOT NULL DEFAULT 'active', -- planned/active/on_hold/completed/cancelled
    manager_id              INTEGER REFERENCES users (id),
    start_date              DATE,
    end_date_planned        DATE,
    end_date_forecast       DATE,
    end_date_actual         DATE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_projects_status ON projects (status);

-- Документы
CREATE TABLE documents (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    code                TEXT NOT NULL,
    title               TEXT NOT NULL,
    discipline          TEXT,
    status              TEXT NOT NULL DEFAULT 'in_work', -- in_work/on_review/approved/archived
    current_revision_id INTEGER NULL,
    created_by          INTEGER NOT NULL REFERENCES users (id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_documents_project_code ON documents (project_id, code);

-- Ревизии документов
CREATE TABLE document_revisions (
    id               SERIAL PRIMARY KEY,
    document_id      INTEGER NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    revision_index   TEXT NOT NULL,    -- 'A01', 'A02', 'B01',...
    revision_letter  TEXT NOT NULL,    -- 'A','B',...
    revision_number  INTEGER NOT NULL, -- 1,2,3...
    version_number   INTEGER NOT NULL, -- монотонный 1..N
    status           TEXT NOT NULL,    -- draft/on_review/approved/superseded
    file_path        TEXT NOT NULL,
    change_log       TEXT,
    created_by       INTEGER NOT NULL REFERENCES users (id),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_by      INTEGER REFERENCES users (id),
    approved_at      TIMESTAMPTZ
);

ALTER TABLE documents
    ADD CONSTRAINT fk_documents_current_revision
    FOREIGN KEY (current_revision_id) REFERENCES document_revisions (id);

CREATE UNIQUE INDEX uq_document_revision_version
    ON document_revisions (document_id, version_number);

CREATE UNIQUE INDEX uq_document_revision_idx
    ON document_revisions (document_id, revision_letter, revision_number);

CREATE INDEX idx_document_revisions_document
    ON document_revisions (document_id);

-- Задачи (планирование)
CREATE TABLE planned_tasks (
    id                      SERIAL PRIMARY KEY,
    project_id              INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    project_code            TEXT NOT NULL,
    project_name            TEXT NOT NULL,
    document_id             INTEGER REFERENCES documents (id) ON DELETE SET NULL,
    document_code           TEXT,
    revision_id             INTEGER REFERENCES document_revisions (id) ON DELETE SET NULL,
    revision_index          TEXT,
    name                    TEXT NOT NULL,
    task_type               TEXT NOT NULL DEFAULT 'engineering', -- engineering/review/approval/other
    assigned_to             INTEGER REFERENCES users (id),
    owner_name              TEXT,
    duration_days_planned   INTEGER NOT NULL DEFAULT 1,
    work_hours_planned      NUMERIC(10,2) NOT NULL DEFAULT 0,
    start_date_planned      DATE,
    end_date_planned        DATE,
    start_date_actual       DATE,
    end_date_actual         DATE,
    percent_complete        INTEGER NOT NULL DEFAULT 0,
    status                  TEXT NOT NULL DEFAULT 'not_started', -- not_started/in_progress/completed/blocked

    -- CPM-поля (offset в днях от начала проекта)
    es                      INTEGER,
    ef                      INTEGER,
    ls                      INTEGER,
    lf                      INTEGER,
    slack                   INTEGER,

    -- фактические часы (кэш для скорости)
    actual_hours            NUMERIC(10,2)
);

CREATE INDEX idx_planned_tasks_project ON planned_tasks (project_id);
CREATE INDEX idx_planned_tasks_assigned_to ON planned_tasks (assigned_to);

-- Зависимости задач
CREATE TABLE task_dependencies (
    id                   SERIAL PRIMARY KEY,
    project_id           INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    predecessor_task_id  INTEGER NOT NULL REFERENCES planned_tasks (id) ON DELETE CASCADE,
    successor_task_id    INTEGER NOT NULL REFERENCES planned_tasks (id) ON DELETE CASCADE,
    dependency_type      TEXT NOT NULL DEFAULT 'FS', -- только FS в MVP
    lag_days             INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_task_dependencies_project ON task_dependencies (project_id);
CREATE INDEX idx_task_dependencies_successor ON task_dependencies (successor_task_id);

-- Учёт времени
CREATE TABLE time_logs (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users (id),
    project_id   INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    document_id  INTEGER REFERENCES documents (id) ON DELETE SET NULL,
    task_id      INTEGER REFERENCES planned_tasks (id) ON DELETE SET NULL,
    day          DATE NOT NULL,
    hours        NUMERIC(6,2) NOT NULL,
    description  TEXT
);

CREATE INDEX idx_time_logs_project_day ON time_logs (project_id, day);
CREATE INDEX idx_time_logs_user_day ON time_logs (user_id, day);

-- Метрики инженеров (для геймификации, в MVP можно пустыми)
CREATE TABLE engineer_metrics (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users (id) UNIQUE,
    total_points     INTEGER NOT NULL DEFAULT 0,
    xp               INTEGER NOT NULL DEFAULT 0,
    rank             TEXT NOT NULL DEFAULT 'junior',
    tasks_completed  INTEGER NOT NULL DEFAULT 0,
    documents_closed INTEGER NOT NULL DEFAULT 0,
    last_updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- События геймификации (MVP: просто журнал)
CREATE TABLE gamification_events (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users (id),
    project_id    INTEGER REFERENCES projects (id) ON DELETE SET NULL,
    event_type    TEXT NOT NULL,
    points_delta  INTEGER NOT NULL,
    xp_delta      INTEGER NOT NULL,
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_gamification_events_user ON gamification_events (user_id);

-- Вспомогательные тестовые данные (опционально)
INSERT INTO users (login, full_name, role, rank) VALUES
('ivan.petrov', 'Иван Петров', 'engineer', 'senior'),
('maria.kuznetsova', 'Мария Кузнецова', 'manager', 'lead'),
('oleg.smirnov', 'Олег Смирнов', 'engineer', 'middle');