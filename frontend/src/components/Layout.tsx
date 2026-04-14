import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Briefcase, Users, Factory, FileText, CheckCircle, Shield,
  Bell, Sun, Moon, LogOut, ChevronDown, Search, Menu, X
} from 'lucide-react';
import { useState, useEffect } from 'react';
import NotificationBell from './NotificationBell';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Руководитель',
  engineer: 'Инженер',
  norm_controller: 'Нормоконтролёр',
};

// 6 основных разделов системы
const MAIN_SECTIONS = [
  {
    to: '/executive', 
    label: 'Руководители', 
    icon: Briefcase, 
    accent: 'leaders',
    description: 'KPI, риски, обзор портфеля'
  },
  {
    to: '/engineering', 
    label: 'Инженерные группы', 
    icon: Users, 
    accent: 'engineering',
    description: 'Документы, задачи, ревизии'
  },
  {
    to: '/production', 
    label: 'Производство', 
    icon: Factory, 
    accent: 'production',
    description: 'Площадка, акты, контроль'
  },
  { 
    to: '/documents', 
    label: 'Документооборот', 
    icon: FileText, 
    accent: 'docs',
    description: 'Регистрация, архив, журналы'
  },
  { 
    to: '/approvals', 
    label: 'Согласования', 
    icon: CheckCircle, 
    accent: 'approvals',
    description: 'Маршруты, очереди, статусы'
  },
  { 
    to: '/audit', 
    label: 'Аудит и контроль', 
    icon: Shield, 
    accent: 'audit',
    description: 'Traceability, события, доступ'
  },
];

export default function Layout() {
  const { user, isDemo, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  // Загрузка темы при монтировании
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

  const handleLogout = () => { logout(); navigate('/login'); };

  // Получение активного раздела
  const getActiveSection = () => {
    const pathname = location.pathname;
    const section = MAIN_SECTIONS.find(s => pathname.startsWith(s.to));
    return section?.accent || 'leaders';
  };

  const activeAccent = getActiveSection();

  return (
    <div className="flex flex-col h-screen bg-[var(--bg-app)] transition-colors duration-300">
      {/* TOP NAVIGATION BAR */}
      <header className="topbar flex-shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden topbar-action"
            style={{ color: 'var(--topbar-icon)' }}
            aria-label="Меню"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="topbar-brand" style={{ color: 'var(--text-inverse)' }}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] flex items-center justify-center font-bold text-white">
              IRIS
            </div>
            <span className="hidden sm:inline font-semibold" style={{ color: 'var(--text-inverse)' }}>ДокПоток IRIS</span>
            {isDemo && (
              <span className="px-2 py-0.5 text-[10px] font-bold bg-[var(--accent-approvals)] text-[var(--text-inverse)] rounded">
                ДЕМО
              </span>
            )}
          </div>
        </div>

        {/* Поиск */}
        <div className="flex-1 max-w-xl mx-8">
          {searchOpen ? (
            <div className="relative">
              <input
                type="text"
                placeholder="Поиск документов, проектов, задач..."
                className="input w-full pl-10 pr-4 py-2"
                style={{ 
                  backgroundColor: 'var(--bg-topbar-hover)', 
                  borderColor: 'var(--border-dark)',
                  color: 'var(--text-inverse)',
                  '--tw-placeholder-color': 'var(--text-tertiary)' as any
                }}
                autoFocus
                onBlur={() => setSearchOpen(false)}
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--topbar-icon)' }} size={18} />
            </div>
          ) : (
            <button
              onClick={() => setSearchOpen(true)}
              className="topbar-action w-full flex items-center gap-3 px-4 py-2 rounded-md"
              style={{ 
                backgroundColor: 'var(--bg-topbar-hover)',
                color: 'var(--topbar-icon)'
              }}
            >
              <Search size={18} />
              <span className="text-sm">Поиск...</span>
            </button>
          )}
        </div>

        {/* Правая часть */}
        <div className="flex items-center gap-2">
          {/* Переключатель темы */}
          <button
            onClick={toggleTheme}
            className="topbar-action"
            style={{ color: 'var(--topbar-icon)' }}
            aria-label={isDarkMode ? 'Светлый режим' : 'Тёмный режим'}
            title={isDarkMode ? 'Светлый режим' : 'Тёмный режим'}
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          {/* Уведомления */}
          <div className="relative">
            <button
              className="topbar-action"
              style={{ color: 'var(--notification-icon)' }}
              aria-label="Уведомления"
              title="Уведомления"
              onClick={() => navigate('/profile')}
            >
              <Bell size={20} />
              <span 
                className="absolute top-1 right-1 w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: 'var(--notification-badge)' }}
              />
            </button>
          </div>

          {/* Профиль */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md hover:bg-[var(--bg-topbar-hover)] transition-colors"
            >
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm"
                style={{ 
                  backgroundColor: 'var(--primary-light)',
                  color: 'var(--primary)'
                }}
              >
                {user?.full_name?.[0] || 'U'}
              </div>
              <div className="hidden md:block text-left">
                <div className="text-sm font-medium" style={{ color: 'var(--text-inverse)' }}>
                  {user?.full_name || 'Пользователь'}
                </div>
                <div className="text-xs" style={{ color: 'var(--topbar-icon)' }}>
                  {ROLE_LABELS[user?.role || ''] || user?.role}
                </div>
              </div>
              <ChevronDown size={16} style={{ color: 'var(--topbar-icon)' }} />
            </button>

            {userMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setUserMenuOpen(false)}
                />
                <div 
                  className="absolute right-0 mt-2 w-56 rounded-lg shadow-xl border z-50 py-1"
                  style={{ 
                    backgroundColor: 'var(--bg-surface)',
                    borderColor: 'var(--border-default)'
                  }}
                >
                  <NavLink
                    to="/profile"
                    className="block px-4 py-2 text-sm hover:bg-[var(--bg-hover)]"
                    style={{ color: 'var(--text-primary)' }}
                    onClick={() => setUserMenuOpen(false)}
                  >
                    Профиль
                  </NavLink>
                  <NavLink
                    to="/settings"
                    className="block px-4 py-2 text-sm hover:bg-[var(--bg-hover)]"
                    style={{ color: 'var(--text-primary)' }}
                    onClick={() => setUserMenuOpen(false)}
                  >
                    Настройки
                  </NavLink>
                  {user?.role === 'admin' && (
                    <NavLink
                      to="/admin/users"
                      className="block px-4 py-2 text-sm hover:bg-[var(--bg-hover)]"
                      style={{ color: 'var(--text-primary)' }}
                      onClick={() => setUserMenuOpen(false)}
                    >
                      Администрирование
                    </NavLink>
                  )}
                  <hr className="my-1" style={{ borderColor: 'var(--border-light)' }} />
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm flex items-center gap-2"
                    style={{ color: 'var(--error)' }}
                  >
                    <LogOut size={16} />
                    Выйти
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      {/* MAIN SECTIONS TABS */}
      <nav 
        className="border-b flex-shrink-0"
        style={{ 
          backgroundColor: 'var(--bg-surface)',
          borderColor: 'var(--border-default)'
        }}
      >
        <div className="max-w-[1920px] mx-auto px-4">
          <div className="flex items-center gap-1 overflow-x-auto custom-scrollbar">
            {MAIN_SECTIONS.map((section) => {
              const Icon = section.icon;
              const isActive = location.pathname.startsWith(section.to);
              
              return (
                <NavLink
                  key={section.to}
                  to={section.to}
                  className={`section-tab section-tab-${section.accent} flex items-center gap-2 whitespace-nowrap ${
                    isActive ? 'active' : ''
                  }`}
                  title={section.description}
                >
                  <Icon size={16} />
                  <span className="hidden lg:inline">{section.label}</span>
                </NavLink>
              );
            })}
          </div>
        </div>
      </nav>

      {/* MOBILE MENU */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50 pt-16" style={{ backgroundColor: 'var(--bg-app)' }}>
          <nav className="p-4 space-y-2">
            {MAIN_SECTIONS.map((section) => {
              const Icon = section.icon;
              const isActive = location.pathname.startsWith(section.to);
              
              return (
                <NavLink
                  key={section.to}
                  to={section.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? `bg-[var(--accent-${section.accent}-light)]`
                      : 'hover:bg-[var(--bg-hover)]'
                  }`}
                  style={{ color: isActive ? `var(--accent-${section.accent})` : 'var(--text-primary)' }}
                >
                  <Icon size={20} />
                  <div>
                    <div className="font-medium">{section.label}</div>
                    <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{section.description}</div>
                  </div>
                </NavLink>
              );
            })}
          </nav>
        </div>
      )}

      {/* PAGE CONTENT */}
      <main className="flex-1 overflow-auto custom-scrollbar">
        <div className="max-w-[1920px] mx-auto p-4 lg:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
