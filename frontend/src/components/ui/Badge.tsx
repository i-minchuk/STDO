import React, { ReactNode } from 'react';

interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'leaders' | 'engineering' | 'production' | 'docs' | 'approvals' | 'audit';
  children: ReactNode;
  className?: string;
  leftIcon?: ReactNode;
  dot?: boolean;
}

export default function Badge({ 
  children, 
  variant = 'neutral',
  className = '', 
  leftIcon,
  dot = false
}: BadgeProps) {
  const variants = {
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
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
    >
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      {children}
    </span>
  );
}
