import { ReactNode, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface SidebarProps {
  children: ReactNode;
  defaultCollapsed?: boolean;
}

/**
 * Сворачиваемая боковая панель
 * Используется на экране списка документов для статистики
 */
export function Sidebar({ children, defaultCollapsed = false }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  return (
    <div className="relative">
      {/* Кнопка сворачивания */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -left-3 top-4 z-10 w-6 h-6 bg-[var(--bg-card)] border border-[var(--border)] rounded-full flex items-center justify-center hover:bg-[var(--bg-hover)] transition-colors shadow-sm"
        aria-label={isCollapsed ? 'Развернуть панель' : 'Свернуть панель'}
        aria-expanded={!isCollapsed}
      >
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4 text-[var(--text-muted)]" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-[var(--text-muted)]" />
        )}
      </button>

      {/* Панель */}
      <div
        className={`
          bg-[var(--bg-card)] border border-[var(--border)] rounded-lg
          transition-all duration-300 overflow-hidden
          ${isCollapsed ? 'w-0 p-0 opacity-0' : 'w-full max-w-[280px] p-4 opacity-100'}
        `}
      >
        <div className="space-y-4">
          {children}
        </div>
      </div>
    </div>
  );
}

/**
 * Карточка статистики для боковой панели
 */
interface StatsCardProps {
  title: string;
  items: Array<{
    label: string;
    value: number | string;
    color?: 'default' | 'success' | 'warning' | 'error' | 'info';
  }>;
}

export function StatsCard({ title, items }: StatsCardProps) {
  const colorClasses = {
    default: 'text-[var(--text-base)]',
    success: 'text-[var(--success)]',
    warning: 'text-[var(--warning)]',
    error: 'text-[var(--error)]',
    info: 'text-[var(--info)]',
  };

  return (
    <div>
      <h3 className="text-sm font-semibold text-[var(--text-base)] mb-3">
        {title}
      </h3>
      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.label}
            className="flex justify-between items-center text-sm"
          >
            <span className="text-[var(--text-muted)]">{item.label}</span>
            <span className={`font-medium ${colorClasses[item.color || 'default']}`}>
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
