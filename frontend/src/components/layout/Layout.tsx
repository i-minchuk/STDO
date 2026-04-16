import { useEffect, useRef, useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Moon, Sun, Bell, User, LogOut, ChevronDown } from 'lucide-react';

interface LayoutProps {
  children?: React.ReactNode;
}

const navItems = [
  { to: '/dashboard', label: 'Руководители' },
  { to: '/projects', label: 'Инженерные группы' },
  { to: '/production', label: 'Производство' },
  { to: '/documents', label: 'Документооборот' },
  { to: '/approvals', label: 'Согласования' },
  { to: '/audit', label: 'Аудит' },
];

export default function Layout({ children }: LayoutProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [unreadCount] = useState(3);
  const navigate = useNavigate();
  const location = useLocation();
  const userMenuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    try {
      const savedTheme = localStorage.getItem('iris-theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);

      setIsDarkMode(isDark);
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    } catch {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        userMenuRef.current &&
        event.target instanceof Node &&
        !userMenuRef.current.contains(event.target)
      ) {
        setShowUserMenu(false);
      }
    };

    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEsc);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEsc);
    };
  }, []);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);

    try {
      localStorage.setItem('iris-theme', newMode ? 'dark' : 'light');
    } catch {
      // ignore
    }

    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
  };

  const handleLogout = () => {
    setShowUserMenu(false);
    navigate('/login');
  };

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(`${path}/`);

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: 'var(--bg-app)',
        color: 'var(--text-primary)',
      }}
    >
      <header
        className="sticky top-0 z-50 border-b backdrop-blur"
        style={{
          backgroundColor: 'var(--bg-topbar)',
          borderColor: 'var(--border-default)',
        }}
      >
        <div className="flex h-14 items-center justify-between px-4 md:px-6">
          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="flex items-center gap-3 no-underline">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold shadow-sm"
                style={{
                  background:
                    'linear-gradient(135deg, var(--accent-leaders), var(--accent-docs))',
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

            <nav
              className="hidden items-center gap-1 lg:flex"
              aria-label="Главная навигация"
            >
              {navItems.map((item) => {
                const active = isActive(item.to);

                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className="rounded-md px-3 py-2 text-sm font-medium no-underline transition-colors duration-150"
                    style={{
                      color: 'var(--text-inverse)',
                      backgroundColor: active
                        ? 'var(--topbar-active)'
                        : 'transparent',
                    }}
                    aria-current={active ? 'page' : undefined}
                    onMouseEnter={(e) => {
                      if (!active) {
                        (e.currentTarget as HTMLAnchorElement).style.backgroundColor =
                          'var(--topbar-hover)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLAnchorElement).style.backgroundColor =
                        active ? 'var(--topbar-active)' : 'transparent';
                    }}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleTheme}
              className="flex h-10 w-10 items-center justify-center rounded-md transition-colors duration-150"
              style={{ color: 'var(--topbar-icon)' }}
              aria-label="Переключить тему"
              title={isDarkMode ? 'Светлая тема' : 'Тёмная тема'}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                  'var(--topbar-hover)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                  'transparent';
              }}
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <button
              type="button"
              className="relative flex h-10 w-10 items-center justify-center rounded-md transition-colors duration-150"
              style={{ color: 'var(--notification-icon)' }}
              aria-label="Уведомления"
              title="Уведомления"
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                  'var(--topbar-hover)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                  'transparent';
              }}
            >
              <Bell size={18} />
              {unreadCount > 0 ? (
                <span
                  className="absolute right-1.5 top-1.5 flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[10px] font-semibold leading-none"
                  style={{
                    backgroundColor: 'var(--notification-badge)',
                    color: 'var(--text-inverse)',
                    border: '1px solid var(--bg-topbar)',
                  }}
                >
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              ) : null}
            </button>

            <div className="relative" ref={userMenuRef}>
              <button
                type="button"
                onClick={() => setShowUserMenu((prev) => !prev)}
                className="flex items-center gap-2 rounded-md px-2 py-2 text-sm font-medium transition-colors duration-150"
                style={{ color: 'var(--text-inverse)' }}
                aria-haspopup="menu"
                aria-expanded={showUserMenu}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                    'var(--topbar-hover)';
                }}
                onMouseLeave={(e) => {
                  if (!showUserMenu) {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                      'transparent';
                  }
                }}
              >
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full"
                  style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                >
                  <User size={16} />
                </div>
                <span className="hidden md:inline">Admin</span>
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
                  role="menu"
                >
                  <div
                    className="border-b px-4 py-3"
                    style={{ borderColor: 'var(--border-default)' }}
                  >
                    <div className="font-semibold">Admin User</div>
                    <div
                      className="text-sm"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      admin@stdo-demo.com
                    </div>
                  </div>

                  <div className="p-2">
                    <button
                      type="button"
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors duration-150"
                      style={{ color: 'var(--text-primary)' }}
                      role="menuitem"
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                          'var(--topbar-hover)';
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                          'transparent';
                      }}
                    >
                      <User size={16} />
                      Профиль
                    </button>

                    <button
                      type="button"
                      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors duration-150"
                      style={{ color: 'var(--error)' }}
                      role="menuitem"
                      onClick={handleLogout}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                          'var(--topbar-hover)';
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                          'transparent';
                      }}
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
      </header>

      <main className="px-4 py-6 md:px-6">{children ?? <Outlet />}</main>
    </div>
  );
}