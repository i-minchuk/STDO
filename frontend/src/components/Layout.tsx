import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, FileText, ListTodo, Trophy, UserCircle,
  Users, LogOut, Menu, X, BarChart3, Upload, ClipboardCheck
} from 'lucide-react';
import { useState } from 'react';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Руководитель',
  engineer: 'Инженер',
  norm_controller: 'Нормоконтролёр',
};

export default function Layout() {
  const { user, isDemo, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => { logout(); navigate('/login'); };

  const links = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Дашборд' },
    { to: '/documents', icon: FileText, label: 'Документы' },
    { to: '/tasks', icon: ListTodo, label: 'Задачи' },
    { to: '/import', icon: Upload, label: 'Импорт Excel' },
    { to: '/workload', icon: BarChart3, label: 'Загруженность' },
    { to: '/tender', icon: ClipboardCheck, label: 'Оценка тендера' },
    { to: '/leaderboard', icon: Trophy, label: 'Лидерборд' },
    { to: '/profile', icon: UserCircle, label: 'Мой кабинет' },
  ];

  if (user?.role === 'admin') {
    links.push({ to: '/admin/users', icon: Users, label: 'Пользователи' });
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-900 text-white flex flex-col transition-all duration-200 flex-shrink-0`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-wide">СТДО</span>
              {isDemo && <span className="text-[10px] bg-yellow-500 text-black px-1.5 py-0.5 rounded font-bold">ДЕМО</span>}
            </div>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-400 hover:text-white">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        <nav className="flex-1 py-4 space-y-1 overflow-y-auto">
          {links.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <Icon size={20} />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-gray-700 p-4">
          {sidebarOpen && user && (
            <div className="mb-3">
              <div className="text-sm font-medium">{user.full_name}</div>
              <div className="text-xs text-gray-400">{ROLE_LABELS[user.role] || user.role}</div>
            </div>
          )}
          <button onClick={handleLogout} className="flex items-center gap-2 text-gray-400 hover:text-red-400 text-sm w-full">
            <LogOut size={18} />
            {sidebarOpen && <span>Выйти</span>}
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <Outlet />
      </main>
    </div>
  );
}
