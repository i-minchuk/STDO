interface AvatarProps {
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Аватар пользователя
 * Показывает инициалы, если нет фото
 */
export function Avatar({ name, size = 'md', className = '' }: AvatarProps) {
  const sizes = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base',
  };

  // Получаем инициалы
  const initials = name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  // Генерируем цвет на основе имени (детерминированно)
  const getColor = (name: string) => {
    const colors = [
      'var(--primary)',
      'var(--success)',
      'var(--info)',
      'var(--warning)',
      'var(--secondary)',
    ];
    const index = name.length % colors.length;
    return colors[index];
  };

  const bgColor = getColor(name);

  return (
    <div
      className={`${sizes[size]} rounded-full flex items-center justify-center font-medium text-white ${className}`}
      style={{ backgroundColor: bgColor }}
      title={name}
    >
      {initials}
    </div>
  );
}
