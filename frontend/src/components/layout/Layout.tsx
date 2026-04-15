import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Moon, Sun, Bell, User, LogOut, ChevronDown } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { to: '/dashboard', label: 'Руководители' },
  { to: '/projects', label: 'Инженерные группы' },
  { to: '/production', label: 'Производство' },
  { to: '/documents', label: 'Документооборот' },
  { to: '/approvals', label: 'Согласования' },
  { to: '/audit', label: 'Аудит и контроль' },
];

export function Layout({ children }: LayoutProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const savedTheme = localStorage.getItem('iris-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

    setIsDarkMode(isDark);
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('iris-theme', newMode ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
  };

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: 'var(--bg-app)',
        color: 'var(--text-primary)',
      }}
    >
      <header
        className="sticky top-0 z-50 border-b"
        style={{
          backgroundColor: 'var(--bg-topbar)',
          borderColor: 'var(--border-default)',
        }}
      >
        <div className="flex h-14 items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="flex items-center gap-3 no-underline">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold"
                style={{
                  background: 'linear-gradient(135deg, var(--primary), var(--accent-leaders))',
                  color: 'var(--text-inverse)',
                }}
              >
                IRIS
              </div>
              <div
                className="text-lg font-semibold tracking-tight"
                style={{ color: 'var(--text-inverse)' }}
              >
                ДокПоток IRIS
              </div>
            </Link>

            <div className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className="rounded-md px-3 py-2 text-sm font-medium transition-colors no-underline"
                  style={{ color: 'var(--text-inverse)' }}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Поиск..."
              className="hidden md:block h-10 rounded-md border px-3 text-sm outline-none transition-colors"
              style={{
                backgroundColor: 'rgba(255,255,255,0.06)',
                borderColor: 'rgba(255,255,255,0.08)',
                color: 'var(--text-inverse)',
              }}
            />

            <button
              type="button"
              onClick={toggleTheme}
              className="flex h-10 w-10 items-center justify-center rounded-md transition-colors"
              style={{ color: 'var(--topbar-icon)' }}
              aria-label="Переключить тему"
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <button
              type="button"
              className="relative flex h-10 w-10 items-center justify-center rounded-md transition-colors"
              style={{ color: 'var(--notification-icon)' }}
              aria-label="Уведомления"
            >
              <Bell size={18} />
              <span
                className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: 'var(--notification-badge)' }}
              />
            </button>

            <div className="relative">
              <button
                type="button"
                onClick={() => setShowUserMenu((prev) => !prev)}
                className="flex items-center gap-2 rounded-md px-2 py-2 transition-colors"
                style={{ color: 'var(--text-inverse)' }}
                aria-label="Профиль"
                aria-expanded={showUserMenu}
              >
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full"
                  style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                >
                  <User size={16} />
                </div>
                <span className="hidden md:inline text-sm font-medium">Admin</span>
                <ChevronDown size={16} />
              </button>

              {showUserMenu ? (
                <div
                  className="absolute right-0 mt-2 w-64 rounded-lg border shadow-lg"
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    borderColor: 'var(--border-default)',
                    color: 'var(--text-primary)',
                  }}
                >
                  <div className="border-b px-4 py-3" style={{ borderColor: 'var(--border-default)' }}>
                    <div className="font-semibold">Admin User</div>
                    <div style={{ color: 'var(--text-secondary)' }} className="text-sm">
                      admin@stdo-demo.com
                    </div>
                  </div>

                  <div className="p-2">
                    <button
                      type="button"
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors"
                      style={{ color: 'var(--text-primary)' }}
                      onClick={() => {
                        setShowUserMenu(false);
                        navigate('/profile');
                      }}
                    >
                      <User size={16} />
                      Профиль
                    </button>

                    <button
                      type="button"
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors"
                      style={{ color: 'var(--error)' }}
                      onClick={handleLogout}
                    >
                      <LogOut size={16} />
                      Выйти
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <div
          className="flex overflow-x-auto border-t px-2 py-1 lg:hidden"
          style={{ borderColor: 'rgba(255,255,255,0.08)' }}
        >
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium no-underline"
              style={{ color: 'var(--text-inverse)' }}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </header>

      <main className="px-4 py-6 md:px-6">{children}</main>

      <footer
        className="border-t px-6 py-4 text-sm"
        style={{
          borderColor: 'var(--border-default)',
          color: 'var(--text-secondary)',
        }}
      >
        © 2026 ДокПоток IRIS. Версия 0.3.0
      </footer>
    </div>
  );
}