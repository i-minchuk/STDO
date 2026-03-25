export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'engineer' | 'norm_controller';
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Project {
  id: number;
  number: string;
  name: string;
  status: string;
  customer: string;
  start_date: string | null;
  end_date_plan: string | null;
  total_tasks: number;
  completed_tasks: number;
  spi: number | null;
  risk_level: 'low' | 'medium' | 'high';
}

export interface PortfolioSummary {
  total: number;
  active: number;
  at_risk: number;
  completed: number;
}

export interface Document {
  id: number;
  code: string;
  title: string;
  project_id: number;
  status: string;
  doc_type: string;
  current_revision_id: number | null;
}

export interface Revision {
  id: number;
  letter: string;
  number: number;
  status: string;
  created_at: string | null;
  file_path: string | null;
}

export interface DocumentDetail extends Document {
  revisions: Revision[];
}

export interface Task {
  id: number;
  project_id: number;
  document_id: number | null;
  task_type: string | null;
  title: string;
  status: string;
  planned_start: string | null;
  planned_finish: string | null;
  planned_hours: number;
  actual_hours: number;
  percent_complete: number;
  engineer: string | null;
  is_critical: boolean;
  es: number | null;
  ef: number | null;
  ls: number | null;
  lf: number | null;
  slack: number | null;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  full_name: string;
  score: number;
  level: number;
  level_title: string;
  badges_count: number;
}

export interface GamificationProfile {
  user_id: number;
  username: string;
  full_name: string;
  score: number;
  level: number;
  level_title: string;
  badges: string[];
  next_level_at: number | null;
}

export interface Badge {
  id: string;
  name: string;
  desc: string;
}

export interface ProjectHealth {
  project: { id: number; name: string; number: string };
  spi: number | null;
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  critical_tasks: number;
  overdue_tasks: number;
  risk_level: string;
}

export interface EngineerSPI {
  engineer: string;
  total_tasks: number;
  completed_tasks: number;
  spi: number | null;
}
