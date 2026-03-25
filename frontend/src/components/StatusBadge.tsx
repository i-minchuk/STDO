const STATUS_STYLES: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-gray-100 text-gray-800',
  not_started: 'bg-gray-100 text-gray-600',
  on_review: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  draft: 'bg-gray-100 text-gray-600',
  archived: 'bg-gray-200 text-gray-500',
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
};

const STATUS_LABELS: Record<string, string> = {
  active: 'Активный',
  in_progress: 'В работе',
  completed: 'Завершён',
  not_started: 'Не начата',
  on_review: 'На проверке',
  approved: 'Утверждён',
  draft: 'Черновик',
  archived: 'Архив',
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
};

export default function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] || 'bg-gray-100 text-gray-700';
  const label = STATUS_LABELS[status] || status;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}
