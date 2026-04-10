type StatusBadgeProps = {
  status?: string;
};

const STATUS_MAP: Record<string, string> = {
  active: "bg-blue-100 text-blue-700",
  archived: "bg-gray-100 text-gray-700",
  completed: "bg-green-100 text-green-700",
  inprogress: "bg-amber-100 text-amber-700",
  notstarted: "bg-slate-100 text-slate-700",
  overdue: "bg-red-100 text-red-700",
  low: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-red-100 text-red-700",
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