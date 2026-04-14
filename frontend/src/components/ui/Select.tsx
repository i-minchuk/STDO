import React from 'react';

interface SelectOption {
  value: string | number;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
}

export default function Select({ label, id, options, error, className = '', ...props }: SelectProps) {
  const selectId = id || (label ? `select-${label.replace(/\s+/g, '-').toLowerCase()}` : undefined);
  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={selectId} className="block text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`block w-full pl-3 pr-10 py-2 text-base border focus:outline-none focus:ring-1 sm:text-sm rounded-md shadow-sm ${className}`}
        style={{ 
          backgroundColor: 'var(--bg-surface)',
          borderColor: error ? 'var(--error)' : 'var(--border-default)',
          color: 'var(--text-primary)'
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-xs" style={{ color: 'var(--error)' }}>{error}</p>}
    </div>
  );
}
