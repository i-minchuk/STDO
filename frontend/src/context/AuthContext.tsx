import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User } from '../types';
import { login as apiLogin, getMe } from '../api/auth';

const DEMO_USER: User = {
  id: 1,
  username: 'admin',
  email: 'admin@stdo.local',
  full_name: 'Администратор',
  role: 'admin',
  is_active: true,
};

interface AuthCtx {
  user: User | null;
  loading: boolean;
  isDemo: boolean;
  login: (username: string, password: string) => Promise<void>;
  loginDemo: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx>({} as AuthCtx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    // Check demo mode first
    if (localStorage.getItem('demo_mode') === 'true') {
      setUser(DEMO_USER);
      setIsDemo(true);
      setLoading(false);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (token) {
      getMe().then(setUser).catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const tokens = await apiLogin(username, password);
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.removeItem('demo_mode');
    setIsDemo(false);
    const me = await getMe();
    setUser(me);
  };

  const loginDemo = () => {
    localStorage.setItem('demo_mode', 'true');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsDemo(true);
    setUser(DEMO_USER);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('demo_mode');
    setIsDemo(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isDemo, login, loginDemo, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
