import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export default function Card({ children, padding = 'md', className = '', ...props }: CardProps) {
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div 
      className={`bg-bg-card rounded-xl shadow-sm border border-border-light ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
