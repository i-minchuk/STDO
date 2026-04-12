-- ============================================================================
-- ⚠️ MIGRATED TO ALEMBIC ⚠️
-- ============================================================================
-- This SQL migration has been consolidated into Alembic revision:
-- alembic/versions/87350b5f2a4a_add_performance_indexes.py
-- 
-- DO NOT RUN THIS FILE DIRECTLY
-- Use: alembic upgrade head
-- ============================================================================

-- Migration: Add indexes to prevent N+1 query performance issues
-- [ORIGINAL] Run: python -m db.migrations_runner
-- [ORIGINAL] or: psql -d iris -f db/migrations/002_add_performance_indexes.sql

-- ============================================================================
-- INDEXES FOR DOCUMENTS
-- ============================================================================

-- Critical: Documents filtered by project_id (used in list_all, get_by_project_id)
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);

-- Documents filtered by status (used in status filtering)
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

-- Documents filtered by code (used in lookups)
CREATE INDEX IF NOT EXISTS idx_documents_code ON documents(code);

-- Documents sorted by created_at (used in ordering)
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- Composite: project + status (common filter combination)
CREATE INDEX IF NOT EXISTS idx_documents_project_status ON documents(project_id, status);

-- ============================================================================
-- INDEXES FOR PLANNED_TASKS
-- ============================================================================

-- Critical: Tasks filtered by project_id (used in EVERY project dashboard query)
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON planned_tasks(project_id);

-- Tasks filtered by status (used in progress calculations)
CREATE INDEX IF NOT EXISTS idx_tasks_status ON planned_tasks(status);

-- Tasks filtered by assigned_to (used in workload views)
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON planned_tasks(assigned_to);

-- Tasks filtered by dates (used in scheduling)
CREATE INDEX IF NOT EXISTS idx_tasks_dates ON planned_tasks(start_date_planned, end_date_planned);

-- Composite: project + status + deadline (common dashboard query)
CREATE INDEX IF NOT EXISTS idx_tasks_project_status_deadline ON planned_tasks(project_id, status, end_date_planned);

-- Composite: project + revision (used in revision workflow)
CREATE INDEX IF NOT EXISTS idx_tasks_project_revision ON planned_tasks(project_id, revision_id);

-- ============================================================================
-- INDEXES FOR TASK_DEPENDENCIES
-- ============================================================================

-- Dependencies filtered by project (used in CPM scheduling)
CREATE INDEX IF NOT EXISTS idx_deps_project_id ON task_dependencies(project_id);

-- Dependencies for specific task (used in dependency resolution)
CREATE INDEX IF NOT EXISTS idx_deps_predecessor ON task_dependencies(predecessor_task_id);
CREATE INDEX IF NOT EXISTS idx_deps_successor ON task_dependencies(successor_task_id);

-- ============================================================================
-- INDEXES FOR DOCUMENT_REVISIONS
-- ============================================================================

-- Revisions for document (used in version tracking)
CREATE INDEX IF NOT EXISTS idx_revisions_document_id ON document_revisions(document_id);

-- Revisions by status (used in workflow)
CREATE INDEX IF NOT EXISTS idx_revisions_status ON document_revisions(status);

-- ============================================================================
-- INDEXES FOR REMARKS
-- ============================================================================

-- Remarks by project (used in project comments)
CREATE INDEX IF NOT EXISTS idx_remarks_project_id ON remarks(project_id);

-- Remarks by status (used in filtering)
CREATE INDEX IF NOT EXISTS idx_remarks_status ON remarks(status);

-- Remarks by assignee (used in workload)
CREATE INDEX IF NOT EXISTS idx_remarks_assignee ON remarks(assignee_id);

-- ============================================================================
-- INDEXES FOR USERS
-- ============================================================================

-- User lookups by username (used in auth)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- User lookups by email (used in auth)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- INDEXES FOR PROJECTS
-- ============================================================================

-- Projects by status + manager (used in dashboard filtering)
CREATE INDEX IF NOT EXISTS idx_projects_status_manager ON projects(status, manager_id);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- After running migration, verify indexes were created:
-- SELECT indexname, tablename FROM pg_indexes 
-- WHERE tablename IN ('documents', 'planned_tasks', 'task_dependencies', 
--                     'document_revisions', 'remarks', 'users', 'projects')
-- ORDER BY tablename, indexname;

-- Check for unused indexes after 1 week:
-- SELECT schemaname, tablename, indexname, idx_scan
-- FROM pg_stat_user_indexes
-- WHERE idx_scan = 0
-- AND tablename IN ('documents', 'planned_tasks', 'task_dependencies', 
--                   'document_revisions', 'remarks', 'users', 'projects');
