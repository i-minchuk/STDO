import type { ReactNode } from 'react';

type BadgeVariant =
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'neutral'
  | 'leaders'
  | 'engineering'
  | 'production'
  | 'docs'
  | 'approvals'
  | 'audit';

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
  leftIcon?: ReactNode;
  dot?: boolean;
}

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

export default function Badge({
  children,
  variant = 'neutral',
  className = '',
  leftIcon,
  dot = false,
}: BadgeProps) {
  const variants: Record<BadgeVariant, string> = {
    success: 'bg-[var(--success-light)] text-[var(--success)]',
    warning: 'bg-[var(--warning-light)] text-[var(--warning)]',
    error: 'bg-[var(--error-light)] text-[var(--error)]',
    info: 'bg-[var(--info-light)] text-[var(--info)]',
    neutral: 'bg-[var(--bg-hover)] text-[var(--text-secondary)]',
    leaders: 'bg-[var(--accent-leaders-light)] text-[var(--accent-leaders)]',
    engineering: 'bg-[var(--accent-engineering-light)] text-[var(--accent-engineering)]',
    production: 'bg-[var(--accent-production-light)] text-[var(--accent-production)]',
    docs: 'bg-[var(--accent-docs-light)] text-[var(--accent-docs)]',
    approvals: 'bg-[var(--accent-approvals-light)] text-[var(--accent-approvals)]',
    audit: 'bg-[var(--accent-audit-light)] text-[var(--accent-audit)]',
  };

  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium leading-none',
        variants[variant],
        className
      )}
    >
      {dot ? (
        <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" aria-hidden="true" />
      ) : null}
      {leftIcon ? <span className="inline-flex">{leftIcon}</span> : null}
      <span>{children}</span>
    </span>
  );
}