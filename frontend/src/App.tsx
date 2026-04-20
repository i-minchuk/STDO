import { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './context/useAuth';

const Login = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Documents = lazy(() => import('./pages/Documents'));
const DocumentCreate = lazy(() => import('./pages/DocumentCreate'));
const Projects = lazy(() => import('./pages/Projects'));
const ImportExcel = lazy(() => import('./pages/ImportExcel'));
const Achievements = lazy(() => import('./pages/Achievements'));
const NotFound = lazy(() => import('./pages/NotFound'));
const DocumentWorkspace = lazy(() => import('./components/workspace/DocumentWorkspace'));
const Layout = lazy(() => import('./components/Layout'));

function PageLoader() {
  return (
    <div
      className="flex min-h-[40vh] items-center justify-center"
      style={{ color: 'var(--text-secondary)' }}
    >
      <div className="flex flex-col items-center gap-3">
        <div
          className="h-10 w-10 animate-spin rounded-full border-4 border-solid border-gray-300 border-t-transparent"
          aria-hidden="true"
        />
        <p className="text-sm">Загрузка страницы...</p>
      </div>
    </div>
  );
}

function AppShell({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <PageLoader />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              <AppShell>
                <Login />
              </AppShell>
            }
          />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />

            <Route
              path="dashboard"
              element={
                <AppShell>
                  <Dashboard />
                </AppShell>
              }
            />

            <Route
              path="projects"
              element={
                <AppShell>
                  <Projects />
                </AppShell>
              }
            />

            <Route
              path="documents"
              element={
                <AppShell>
                  <Documents />
                </AppShell>
              }
            />

            <Route
              path="documents/new"
              element={
                <AppShell>
                  <DocumentCreate />
                </AppShell>
              }
            />

            <Route
              path="import"
              element={
                <AppShell>
                  <ImportExcel />
                </AppShell>
              }
            />

            <Route
              path="achievements"
              element={
                <AppShell>
                  <Achievements />
                </AppShell>
              }
            />

            <Route
              path="*"
              element={
                <AppShell>
                  <NotFound />
                </AppShell>
              }
            />
          </Route>

          <Route
            path="/documents/workspace/:projectId"
            element={
              <ProtectedRoute>
                <DocumentWorkspace />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}