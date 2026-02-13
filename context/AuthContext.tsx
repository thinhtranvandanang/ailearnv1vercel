
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { UserOut, LoginRequest, UserCreate } from '../types/auth.types.ts';
import * as authService from '../services/auth.service.ts';
import * as studentService from '../services/student.service.ts';

interface AuthContextType {
  user: UserOut | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  logout: () => void;
  setTokenManually: (token: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getSafeStorage = (key: string) => {
  try {
    return localStorage.getItem(key);
  } catch (e) {
    console.warn("Storage access restricted", e);
    return null;
  }
};

const setSafeStorage = (key: string, value: string) => {
  try {
    localStorage.setItem(key, value);
  } catch (e) {
    console.warn("Storage write restricted", e);
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserOut | null>(() => {
    const savedUser = getSafeStorage('edunexia_user');
    try {
      return savedUser ? JSON.parse(savedUser) : null;
    } catch { return null; }
  });
  const [token, setToken] = useState<string | null>(() => {
    // 1. Check URL for token (priority for Google Redirect)
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      setSafeStorage('edunexia_token', urlToken);
      return urlToken;
    }
    // 2. Fallback to localStorage
    return getSafeStorage('edunexia_token');
  });
  const [isLoading, setIsLoading] = useState(false);

  const fetchProfile = useCallback(async () => {
    if (!token) return;
    try {
      const res = await studentService.getMe();
      if (res.status === 'success' && res.data) {
        setUser(res.data);
        setSafeStorage('edunexia_user', JSON.stringify(res.data));
      }
    } catch (error) {
      console.error("Auth: Failed to fetch profile", error);
    }
  }, [token]);

  useEffect(() => {
    if (token && !user) {
      fetchProfile();
    }
  }, [token, user, fetchProfile]);

  const handleAuthSuccess = (data: any) => {
    const { access_token, user: userData } = data;
    setToken(access_token);
    setUser(userData || null);
    setSafeStorage('edunexia_token', access_token);
    if (userData) {
      setSafeStorage('edunexia_user', JSON.stringify(userData));
    }
  };

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      const response = await authService.login(credentials);
      if (response.status === 'success' && response.data) {
        handleAuthSuccess(response.data);
      } else {
        throw new Error(response.message || 'Đăng nhập thất bại');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: UserCreate) => {
    setIsLoading(true);
    try {
      const response = await authService.register(data);
      if (response.status === 'success' && response.data) {
        handleAuthSuccess(response.data);
      } else {
        throw new Error(response.message || 'Đăng ký thất bại');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const setTokenManually = (newToken: string) => {
    setSafeStorage('edunexia_token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem('edunexia_token');
      localStorage.removeItem('edunexia_user');
    } catch { }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, setTokenManually }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
