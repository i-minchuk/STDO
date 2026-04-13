type StatusBadgeProps = {
  status?: string;
};

const STATUS_MAP: Record<string, string> = {
  active: "bg-info-100 text-info-700",
  archived: "bg-secondary-100 text-secondary-700",
  completed: "bg-success-100 text-success-700",
  inprogress: "bg-warning-100 text-warning-700",
  notstarted: "bg-secondary-100 text-secondary-700",
  overdue: "bg-error-100 text-error-700",
  low: "bg-success-100 text-success-700",
  medium: "bg-warning-100 text-warning-700",
  high: "bg-error-100 text-error-700",
};

const LABEL_MAP: Record<string, string> = {
  active: "Active",
  archived: "Archived",
  completed: "Completed",
  inprogress: "In progress",
  notstarted: "Not started",
  overdue: "Overdue",
  low: "Low",
  medium: "Medium",
  high: "High",
};

export default function StatusBadge({ status = "unknown" }: StatusBadgeProps) {
  const key = String(status).toLowerCase().replace(/[\s_-]/g, "");
  const cls = STATUS_MAP[key] ?? "bg-gray-100 text-gray-700";
  const label = LABEL_MAP[key] ?? status;

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${cls}`}>
      {label}
    </span>
  );
}