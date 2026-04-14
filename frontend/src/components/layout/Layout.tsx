import { ReactNode, useState, useEffect } from 'react';
import { Moon, Sun, Bell, User, LogOut, ChevronDown } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const navigate = useNavigate();

  // Загрузка темы из localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('iris-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
    setIsDarkMode(isDark);
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, []);

  // Переключение темы
  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('iris-theme', newMode ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
  };

  // Выход (заглушка)
  const handleLogout = () => {
    // TODO: Реализовать logout
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-card border-b border-[var(--border)] sticky top-0 z-50">
        <div className="px-6 h-16 flex items-center justify-between">
          {/* Логотип */}
          <Link to="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[var(--primary)] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">IR</span>
            </div>
            <span className="text-lg font-semibold text-[var(--text-base)]">
              ДокПоток IRIS
            </span>
          </Link>

          {/* Правая часть хедера */}
          <div className="flex items-center gap-4">
            {/* Переключатель темы */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md hover:bg-[var(--bg-hover)] transition-colors"
              aria-label={isDarkMode ? 'Включить светлый режим' : 'Включить тёмный режим'}
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5 text-[var(--text-muted)]" />
              ) : (
                <Moon className="w-5 h-5 text-[var(--text-muted)]" />
              )}
            </button>

            {/* Уведомления */}
            <button
              className="p-2 rounded-md hover:bg-[var(--bg-hover)] transition-colors relative"
              aria-label="Уведомления"
            >
              <Bell className="w-5 h-5 text-[var(--text-muted)]" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-[var(--error)] rounded-full"></span>
            </button>

            {/* Профиль пользователя */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 p-2 rounded-md hover:bg-[var(--bg-hover)] transition-colors"
                aria-label="Профиль"
                aria-expanded={showUserMenu}
              >
                <div className="w-8 h-8 bg-[var(--primary-light)] rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-[var(--primary)]" />
                </div>
                <ChevronDown className="w-4 h-4 text-[var(--text-muted)]" />
              </button>

              {/* Выпадающее меню */}
              {showUserMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-[var(--bg-card)] rounded-lg shadow-lg border border-[var(--border)] z-20 py-1">
                    <div className="px-4 py-2 border-b border-[var(--border-light)]">
                      <p className="text-sm font-medium text-[var(--text-base)]">
                        Admin User
                      </p>
                      <p className="text-xs text-[var(--text-muted)]">
                        admin@stdo-demo.com
                      </p>
                    </div>
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-sm text-[var(--text-base)] hover:bg-[var(--bg-hover)]"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Профиль
                    </Link>
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm text-[var(--text-base)] hover:bg-[var(--bg-hover)]"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Настройки
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-[var(--error)] hover:bg-[var(--error-light)] flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" />
                      Выйти
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="flex-1 bg-[var(--bg-page)]">
        {children}
      </main>

      {/* Footer (опционально) */}
      <footer className="bg-[var(--bg-card)] border-t border-[var(--border)] py-4 px-6">
        <p className="text-sm text-[var(--text-muted)] text-center">
          © 2026 ДокПоток IRIS. Версия 0.3.0
        </p>
      </footer>
    </div>
  );
}
