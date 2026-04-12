-- ============================================================================
-- ⚠️ MIGRATED TO ALEMBIC ⚠️
-- ============================================================================
-- This SQL migration has been consolidated into Alembic revision:
-- alembic/versions/87350b5f2a4a_add_performance_indexes.py
-- 
-- DO NOT RUN THIS FILE DIRECTLY
-- Use: alembic upgrade head
-- ============================================================================

-- Migration: Additional performance indexes for P1 sprint
-- [ORIGINAL] Run: python -m db.migrations_runner
-- [ORIGINAL] or: psql -d iris -f db/migrations/004_additional_performance_indexes.sql

-- ============================================================================
-- GAMIFICATION - Heavy aggregation queries
-- ============================================================================

-- Leaderboard: SUM(points_delta) GROUP BY user_id
-- Used in: gamification_api.leaderboard, gamification_event_repository.get_user_score
CREATE INDEX IF NOT EXISTS idx_gamification_events_user_points 
    ON gamification_events (user_id) INCLUDE (points_delta);

-- Event count by type (for daily quests)
-- Used in: gamification_event_repository.get_user_event_count
CREATE INDEX IF NOT EXISTS idx_gamification_events_user_type 
    ON gamification_events (user_id, event_type);

-- Events by date range (for weekly/monthly heatmaps)
-- Used in: heatmap_service, gamification reports
CREATE INDEX IF NOT EXISTS idx_gamification_events_created_at 
    ON gamification_events (created_at DESC);

-- Composite for date range + user (heatmap queries)
CREATE INDEX IF NOT EXISTS idx_gamification_events_user_date 
    ON gamification_events (user_id, created_at DESC);

-- ============================================================================
-- NOTIFICATIONS - Frequent count queries
-- ============================================================================

-- Unread count per user (very frequent)
-- Used in: notification_repository.get_unread_count
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread 
    ON notifications (user_id, is_read) WHERE is_read = false;

-- User notifications with pagination (ORDER BY created_at DESC)
-- Used in: notification_repository.get_user_notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_created 
    ON notifications (user_id, created_at DESC);

-- ============================================================================
-- TIME LOGS - Reporting and workload
-- ============================================================================

-- Hours by user + project + date range (labor reports)
-- Used in: time_log_repository.get_hours_by_user_and_project
CREATE INDEX IF NOT EXISTS idx_time_logs_user_project_date 
    ON time_logs (user_id, project_id, day DESC);

-- Hours by project + date range (project reports)
-- Used in: time_log_repository.get_hours_by_project
CREATE INDEX IF NOT EXISTS idx_time_logs_project_date_desc 
    ON time_logs (project_id, day DESC);

-- ============================================================================
-- REMARKS - Project feedback
-- ============================================================================

-- Remarks by project + status (filtering in remarks list)
-- Used in: remark_repository.get_by_project with status filter
CREATE INDEX IF NOT EXISTS idx_remarks_project_status 
    ON remarks (project_id, status);

-- Unresolved remarks count (dashboard)
CREATE INDEX IF NOT EXISTS idx_remarks_unresolved 
    ON remarks (project_id, status) WHERE status != 'resolved';

-- ============================================================================
-- DOCUMENTS - Search and filtering
-- ============================================================================

-- Documents by project + status + created_at (dashboard views)
-- Used in: document_api.list_documents with multiple filters
CREATE INDEX IF NOT EXISTS idx_documents_project_status_created 
    ON documents (project_id, status, created_at DESC);

-- Search by title/code (full-text would be better, but this helps)
CREATE INDEX IF NOT EXISTS idx_documents_title_gin 
    ON documents USING gin(to_tsvector('russian', title));

-- ============================================================================
-- TASKS - Workload and scheduling
-- ============================================================================

-- Tasks by assignee + status + date (workload API)
-- Used in: workload_api.engineer_workload
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_status_date 
    ON planned_tasks (assigned_to, status, start_date_planned);

-- Overdue tasks (not completed + past deadline)
CREATE INDEX IF NOT EXISTS idx_tasks_overdue 
    ON planned_tasks (status, end_date_planned) 
    WHERE status NOT IN ('completed', 'cancelled');

-- ============================================================================
-- DAILY QUESTS - User progress tracking
-- ============================================================================

-- Daily quests by user + date (very frequent lookup)
-- Used in: daily_quest_repository.get_user_daily_quests
CREATE INDEX IF NOT EXISTS idx_daily_quests_user_date 
    ON daily_quests (user_id, date DESC);

-- Completed quests count (quest completion tracking)
CREATE INDEX IF NOT EXISTS idx_daily_quests_user_date_completed 
    ON daily_quests (user_id, date, is_completed) WHERE is_completed = true;

-- ============================================================================
-- BADGES & COMBO ACHIEVEMENTS
-- ============================================================================

-- User badges (ORDER BY awarded_at DESC)
-- Used in: gamification_badge_repository.get_user_badges
CREATE INDEX IF NOT EXISTS idx_badges_user_awarded 
    ON gamification_badges (user_id, awarded_at DESC);

-- Active combos (not expired)
-- Used in: combo_achievement_repository.get_user_active_combos
CREATE INDEX IF NOT EXISTS idx_combo_user_active 
    ON combo_achievements (user_id, combo_type, expires_at) 
    WHERE expires_at > NOW();

-- ============================================================================
-- TENDERS - Status filtering
-- ============================================================================

-- Tenders by status (list filtering)
-- Used in: tender_api.list_tenders with status filter
CREATE INDEX IF NOT EXISTS idx_tenders_status_created 
    ON tenders (status, created_at DESC);

-- ============================================================================
-- VERIFICATION & MONITORING
-- ============================================================================

-- Verify indexes were created:
-- SELECT indexname, tablename, indexdef 
-- FROM pg_indexes 
-- WHERE tablename IN (
--     'gamification_events', 'notifications', 'time_logs', 'remarks',
--     'documents', 'planned_tasks', 'daily_quests', 'gamification_badges',
--     'combo_achievements', 'tenders'
-- )
-- ORDER BY tablename, indexname;

-- Find missing indexes on foreign keys (optional optimization):
-- SELECT
--     tc.table_name, 
--     kcu.column_name, 
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
--   AND tc.table_name NOT IN ('pg_*', 'sql_*');
