import React, { ReactNode } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  isLoading, 
  leftIcon,
  rightIcon,
  className = '', 
  disabled,
  ...props 
}: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] font-medium transition-colors focus-visible:outline-none focus-visible:outline-2 focus-visible:outline-[var(--primary)] focus-visible:outline-offset-2 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    secondary: 'bg-transparent text-[var(--text-secondary)] border border-[var(--border-default)] hover:bg-[var(--bg-hover)] disabled:border-[var(--border-light)] disabled:text-[var(--text-disabled)]',
    success: 'bg-[var(--success)] text-white hover:bg-[#2F855A] disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    danger: 'bg-[var(--error)] text-white hover:bg-[#C53030] disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    ghost: 'bg-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] disabled:text-[var(--text-disabled)]',
  };

  const sizes = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-6 text-base',
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      {children}
      {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
    </button>
  );
}
