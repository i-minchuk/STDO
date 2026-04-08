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
    gray: 'bg-gray-100 text-gray-700 border-gray-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
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
