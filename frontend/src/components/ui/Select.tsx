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
        <label htmlFor={selectId} className="block text-sm font-medium text-text-base">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`block w-full pl-3 pr-10 py-2 text-base border ${error ? 'border-error' : 'border-border'} focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md shadow-sm ${className}`}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-xs text-error">{error}</p>}
    </div>
  );
}
