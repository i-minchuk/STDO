import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({ label, id, error, className = '', ...props }: InputProps) {
  const inputId = id || (label ? `input-${label.replace(/\s+/g, '-').toLowerCase()}` : undefined);
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-1 sm:text-sm ${className}`}
        style={{ 
          backgroundColor: 'var(--bg-surface)',
          borderColor: error ? 'var(--error)' : 'var(--border-default)',
          color: 'var(--text-primary)',
          '--tw-placeholder-color': 'var(--text-tertiary)' as any
        }}
        {...props}
      />
      {error && <p className="mt-1 text-xs" style={{ color: 'var(--error)' }}>{error}</p>}
    </div>
  );
}
