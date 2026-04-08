import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, FileText, ListTodo, Trophy, UserCircle,
  Users, LogOut, Menu, X, BarChart3, Upload, ClipboardCheck, Award, ChevronLeft, ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import NotificationBell from './NotificationBell';
import Breadcrumbs from './Breadcrumbs';
import { Button, Badge } from './ui';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Руководитель',
  engineer: 'Инженер',
  norm_controller: 'Нормоконтролёр',
};

const NAV_GROUPS = [
  {
    title: 'Основное',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Дашборд' },
      { to: '/documents', icon: FileText, label: 'Документы' },
      { to: '/tasks', icon: ListTodo, label: 'Задачи' },
    ],
  },
  {
    title: 'Аналитика и Данные',
    items: [
      { to: '/import', icon: Upload, label: 'Импорт Excel' },
      { to: '/workload', icon: BarChart3, label: 'Загруженность' },
      { to: '/tender', icon: ClipboardCheck, label: 'Оценка тендера' },
    ],
  },
  {
    title: 'Геймификация',
    items: [
      { to: '/achievements', icon: Award, label: 'Достижения' },
      { to: '/leaderboard', icon: Trophy, label: 'Лидерборд' },
    ],
  },
];

export default function Layout() {
  const { user, isDemo, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* SIDEBAR */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white flex flex-col transition-all duration-300 ease-in-out flex-shrink-0 z-50 shadow-xl`}>
        <div className="flex items-center justify-between p-5 border-b border-gray-800 h-16">
          {sidebarOpen ? (
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent tracking-tight">СТДО</span>
              {isDemo && <Badge variant="yellow" className="text-[9px] h-4">ДЕМО</Badge>}
            </div>
          ) : (
            <span className="w-full text-center text-primary-400 font-bold">ST</span>
          )}
        </div>

        <nav className="flex-1 py-6 overflow-y-auto custom-scrollbar">
          {NAV_GROUPS.map((group, idx) => (
            <div key={idx} className="mb-6 px-3">
              {sidebarOpen && <div className="px-3 mb-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">{group.title}</div>}
              <div className="space-y-1">
                {group.items.map(({ to, icon: Icon, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) =>
                      `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        isActive 
                        ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/50' 
                        : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                      }`
                    }
                  >
                    <Icon size={sidebarOpen ? 18 : 20} className={sidebarOpen ? '' : 'mx-auto'} />
                    {sidebarOpen && <span className="font-medium">{label}</span>}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}

          {user?.role === 'admin' && (
            <div className="px-3">
              {sidebarOpen && <div className="px-3 mb-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest">Админ</div>}
              <NavLink
                to="/admin/users"
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                    isActive ? 'bg-primary-600 text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                  }`
                }
              >
                <Users size={sidebarOpen ? 18 : 20} className={sidebarOpen ? '' : 'mx-auto'} />
                {sidebarOpen && <span className="font-medium">Пользователи</span>}
              </NavLink>
            </div>
          )}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <button onClick={handleLogout} className="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-red-950/20 hover:text-red-400 transition-all text-sm w-full">
            <LogOut size={18} className={sidebarOpen ? '' : 'mx-auto'} />
            {sidebarOpen && <span className="font-medium">Выйти</span>}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER */}
        <header className="h-16 bg-white border-b border-gray-200 px-6 flex justify-between items-center z-40 sticky top-0">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)} 
              className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 transition-colors shadow-sm"
            >
              {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
            </button>
            <Breadcrumbs />
          </div>

          <div className="flex items-center gap-6">
            <NotificationBell onNotificationClick={() => navigate('/profile')} />
            <div className="h-8 w-px bg-gray-200"></div>
            <NavLink to="/profile" className="flex items-center gap-3 group">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{user?.full_name}</div>
                <div className="text-xs text-gray-500">{ROLE_LABELS[user?.role || ''] || user?.role}</div>
              </div>
              <div className="h-10 w-10 rounded-full bg-primary-100 border-2 border-white shadow-sm flex items-center justify-center text-primary-700 font-bold group-hover:border-primary-200 transition-all">
                {user?.full_name?.[0] || 'U'}
              </div>
            </NavLink>
          </div>
        </header>

        {/* PAGE CONTENT */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 custom-scrollbar">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
