import React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'gray' | 'blue' | 'green' | 'yellow' | 'red' | 'indigo';
  dot?: boolean;
}

export default function Badge({ 
  children, 
  variant = 'gray', 
  dot = false,
  className = '', 
  ...props 
}: BadgeProps) {
  const variants = {
    gray: 'bg-secondary-100 text-secondary-700 border-secondary-200',
    blue: 'bg-info-100 text-info-700 border-info-200',
    green: 'bg-success-100 text-success-700 border-success-200',
    yellow: 'bg-warning-100 text-warning-700 border-warning-200',
    red: 'bg-error-100 text-error-700 border-error-200',
    indigo: 'bg-primary-100 text-primary-700 border-primary-200',
  };

  return (
    <span 
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${variants[variant]} ${className}`}
      {...props}
    >
      {dot && (
        <span className={`mr-1.5 h-1.5 w-1.5 rounded-full fill-current`} />
      )}
      {children}
    </span>
  );
}
