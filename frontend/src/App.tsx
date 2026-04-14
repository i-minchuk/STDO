import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import DocumentDetail from './pages/DocumentDetail';
import DocumentCreate from './pages/DocumentCreate';
import Tasks from './pages/Tasks';
import Profile from './pages/Profile';
import Leaderboard from './pages/Leaderboard';
import ProjectDetail from './pages/ProjectDetail';
import AdminUsers from './pages/AdminUsers';
import ImportExcel from './pages/ImportExcel';
import Workload from './pages/Workload';
import TenderAssess from './pages/TenderAssess';
import Achievements from './pages/Achievements';
import ColorTest from './pages/ColorTest';
import ProjectsPage from './pages/ProjectsPage';

// Placeholder components for new sections
const ExecutiveSection = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Руководители</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">KPI, риски, обзор портфеля проектов</p>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* KPI Cards - Executive Overview */}
      <div className="kpi-card">
        <div className="kpi-value">12</div>
        <div className="kpi-label">Проектов в работе</div>
        <div className="kpi-trend positive">↑ 2 за месяц</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-value">94%</div>
        <div className="kpi-label">Готовность документации</div>
        <div className="kpi-trend positive">↑ 3% за неделю</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-value">8</div>
        <div className="kpi-label">На согласовании</div>
        <div className="kpi-trend negative">↓ Просрочено 2</div>
      </div>
      <div className="kpi-card">
        <div className="kpi-value">156</div>
        <div className="kpi-label">Замечаний открыто</div>
        <div className="kpi-trend negative">↑ 12 за неделю</div>
      </div>
    </div>
    {/* Executive content will be added */}
    <div className="card">
      <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4"></h2>  {/* Обзор портфеля проектов */}
      <ProjectsPage />
    </div>
  </div>
);

const EngineeringSection = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Инженерные группы</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Документы, задачи, ревизии, рабочие процессы</p>
      </div>
    </div>
    {/* Engineering Workspace + Dense Operations Console */}
    <Documents />
  </div>
);

const ProductionSection = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Производство</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Площадка, акты, контроль, исполнительная документация</p>
      </div>
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <div className="card">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Оперативный контроль</h2>
          {/* Field + Office Hybrid content */}
          <p className="text-[var(--text-secondary)]">Панель мониторинга производства</p>
        </div>
      </div>
      <div>
        <div className="card">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Задачи</h2>
          <Tasks />
        </div>
      </div>
    </div>
  </div>
);

const ApprovalsSection = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Согласования</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Маршруты, очереди, статусы, возвраты</p>
      </div>
    </div>
    {/* Workflow & Approvals Hub */}
    <div className="card">
      <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Очередь на согласование</h2>
      <p className="text-[var(--text-secondary)]">Workflow hub content</p>
    </div>
  </div>
);

const AuditSection = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Аудит и контроль</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Traceability, события, журналы, контроль доступа</p>
      </div>
    </div>
    {/* Compliance & Audit Desk */}
    <div className="card">
      <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Журнал событий</h2>
      <p className="text-[var(--text-secondary)]">Audit log content</p>
    </div>
  </div>
);

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen text-[var(--text-tertiary)]">Загрузка...</div>;
  if (!user) return <Navigate to="/login" />;
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (user?.role !== 'admin') return <Navigate to="/executive" />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/executive" />} />
            
            {/* 6 основных разделов */}
            <Route path="executive" element={<ExecutiveSection />} />
            <Route path="engineering" element={<EngineeringSection />} />
            <Route path="production" element={<ProductionSection />} />
            <Route path="documents" element={<Documents />} />
            <Route path="approvals" element={<ApprovalsSection />} />
            <Route path="audit" element={<AuditSection />} />
            
            {/* Существующие маршруты */}
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="projects/:id" element={<ProjectDetail />} />
            <Route path="projects/:id/documents" element={<Documents />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="documents/new" element={<DocumentCreate />} />
            <Route path="documents/:id" element={<DocumentDetail />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="import" element={<ImportExcel />} />
            <Route path="workload" element={<Workload />} />
            <Route path="tender" element={<TenderAssess />} />
            <Route path="achievements" element={<Achievements />} />
            <Route path="profile" element={<Profile />} />
            <Route path="leaderboard" element={<Leaderboard />} />
            <Route path="admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
            <Route path="color-test" element={<ColorTest />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
