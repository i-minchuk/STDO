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

// Excel Import
export interface ExcelSheet {
  name: string;
  columns: string[];
  total_rows: number;
  preview: Record<string, string>[];
}

export interface ExcelPreview {
  filename: string;
  sheets: ExcelSheet[];
}

export interface TargetField {
  field: string;
  label: string;
  required: boolean;
}

// Workload
export interface EngineerWorkload {
  engineer: string;
  total_tasks: number;
  active_tasks: number;
  completed_tasks: number;
  planned_hours: number;
  actual_hours: number;
  remaining_hours: number;
  capacity_hours: number;
  free_hours: number;
  utilization_pct: number;
  overdue_tasks: number;
  status: 'overloaded' | 'busy' | 'available';
}

export interface WorkloadSummary {
  total_engineers: number;
  overloaded: number;
  busy: number;
  available: number;
}

export interface WorkloadResponse {
  period: { from: string; to: string; work_days: number };
  engineers: EngineerWorkload[];
  summary: WorkloadSummary;
}

// Tender
export interface TenderDoc {
  doc_type: string;
  count: number;
  hours_per_doc: number;
}

export interface TenderRisk {
  level: 'high' | 'medium' | 'low';
  text: string;
}

export interface TenderResult {
  tender: { name: string; customer: string; deadline: string; calendar_days: number; work_days: number };
  requirements: { total_documents: number; total_hours: number; engineers_needed: number; by_type: { doc_type: string; count: number; hours: number }[] };
  team_capacity: { total_engineers: number; available_engineers: number; capacity_hours: number; current_load_hours: number; free_hours: number; utilization_pct: number };
  assessment: { decision: 'GO' | 'RISKY' | 'NO_GO'; decision_label: string; confidence: string; feasibility_pct: number; risks: TenderRisk[] };
}
