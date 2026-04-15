import type { ChangeEventHandler } from 'react';

type SelectValue = string | number;

export interface SelectOption {
  value: SelectValue;
  label: string;
}

export interface SelectProps {
  label?: string;
  id?: string;
  name?: string;
  value?: SelectValue;
  onChange?: ChangeEventHandler<HTMLSelectElement>;
  options: SelectOption[];
  error?: string;
  className?: string;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export default function Select({
  label,
  id,
  name,
  options,
  error,
  className = '',
  value = '',
  onChange,
  required = false,
  disabled = false,
  placeholder,
}: SelectProps) {
  return (
    <div className={className}>
      {label ? (
        <label
          htmlFor={id}
          className="mb-1 block text-sm font-medium"
          style={{ color: 'var(--text-primary)' }}
        >
          {label}
          {required ? <span className="ml-1 text-red-500">*</span> : null}
        </label>
      ) : null}

      <select
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className="w-full rounded-md border px-3 py-2 text-sm outline-none"
        style={{
          backgroundColor: 'var(--bg-surface)',
          borderColor: error ? 'var(--error)' : 'var(--border-default)',
          color: 'var(--text-primary)',
        }}
      >
        {placeholder ? <option value="">{placeholder}</option> : null}

        {options.map((option) => (
          <option key={String(option.value)} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {error ? (
        <p className="mt-1 text-xs" style={{ color: 'var(--error)' }}>
          {error}
        </p>
      ) : null}
    </div>
  );
}