import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, FolderOpen, FileText, ListTodo,
  Trophy, UserCircle, Users, LogOut, Menu, X
} from 'lucide-react';
import { useState } from 'react';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Руководитель',
  engineer: 'Инженер',
  norm_controller: 'Нормоконтролёр',
};

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => { logout(); navigate('/login'); };

  const links = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Дашборд' },
    { to: '/documents', icon: FileText, label: 'Документы' },
    { to: '/tasks', icon: ListTodo, label: 'Задачи' },
    { to: '/leaderboard', icon: Trophy, label: 'Лидерборд' },
    { to: '/profile', icon: UserCircle, label: 'Мой кабинет' },
  ];

  if (user?.role === 'admin') {
    links.push({ to: '/admin/users', icon: Users, label: 'Пользователи' });
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-900 text-white flex flex-col transition-all duration-200`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          {sidebarOpen && <span className="text-lg font-bold tracking-wide">STDO</span>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-gray-400 hover:text-white">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        <nav className="flex-1 py-4 space-y-1">
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

      {/* Main */}
      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <Outlet />
      </main>
    </div>
  );
}
