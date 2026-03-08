import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, checkAuth, login as apiLogin, logout as apiLogout, register as apiRegister, LoginData, RegisterData } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginData) => Promise<{ success: boolean; error?: string }>;
  register: (data: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    const response = await checkAuth();
    if (response.data) {
      setUser(response.data.user);
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (data: LoginData): Promise<{ success: boolean; error?: string }> => {
    const response = await apiLogin(data);
    if (response.data) {
      setUser(response.data.user);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const register = async (data: RegisterData): Promise<{ success: boolean; error?: string }> => {
    const response = await apiRegister(data);
    if (response.data) {
      setUser(response.data.user);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
