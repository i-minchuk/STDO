import type { ReactNode, ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'ghost' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] font-medium transition-colors focus-visible:outline-none focus-visible:outline-2 focus-visible:outline-[var(--border-focus)] focus-visible:outline-offset-2 disabled:cursor-not-allowed';

  const variants: Record<ButtonVariant, string> = {
    primary:
      'bg-[var(--primary)] text-[var(--text-inverse)] hover:bg-[var(--primary-hover)] disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    secondary:
      'bg-transparent text-[var(--text-secondary)] border border-[var(--border-default)] hover:bg-[var(--bg-hover)] disabled:border-[var(--border-light)] disabled:text-[var(--text-disabled)]',
    success:
      'bg-[var(--success)] text-[var(--text-inverse)] hover:opacity-90 disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    danger:
      'bg-[var(--error)] text-[var(--text-inverse)] hover:opacity-90 disabled:bg-[var(--border-dark)] disabled:text-[var(--text-disabled)]',
    ghost:
      'bg-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] disabled:text-[var(--text-disabled)]',
    outline:
      'bg-transparent text-[var(--text-primary)] border border-[var(--border-default)] hover:bg-[var(--bg-hover)] disabled:border-[var(--border-light)] disabled:text-[var(--text-disabled)]',
  };

  const sizes: Record<ButtonSize, string> = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-6 text-base',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      className={cx(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {isLoading && (
        <span
          className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden="true"
        />
      )}

      {!isLoading && leftIcon ? <span className="inline-flex">{leftIcon}</span> : null}
      <span>{children}</span>
      {!isLoading && rightIcon ? <span className="inline-flex">{rightIcon}</span> : null}
    </button>
  );
}