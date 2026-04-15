import type { InputHTMLAttributes } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
  className?: string;
}

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

export default function Input({
  label,
  id,
  error,
  helpText,
  className = '',
  ...props
}: InputProps) {
  return (
    <div className={cn('w-full', className)}>
      {label ? (
        <label
          htmlFor={id}
          className="mb-1 block text-sm font-medium"
          style={{ color: 'var(--text-primary)' }}
        >
          {label}
        </label>
      ) : null}

      <input
        id={id}
        {...props}
        className={cn(
          'w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors',
          error ? 'border-red-500' : ''
        )}
        style={{
          backgroundColor: 'var(--bg-surface)',
          borderColor: error ? 'var(--error)' : 'var(--border-default)',
          color: 'var(--text-primary)',
        }}
      />

      {error ? (
        <p className="mt-1 text-xs" style={{ color: 'var(--error)' }}>
          {error}
        </p>
      ) : helpText ? (
        <p className="mt-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
          {helpText}
        </p>
      ) : null}
    </div>
  );
}