import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../api/client';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<any>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<any>;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    setIsLoading(true);
    try {
      const response = await api.auth.me();
      setUser(response);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('token');
      setUser(null);
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const data = await api.auth.login(email, password);
      localStorage.setItem('token', data.access_token);
      setUser(data.user);
      toast.success('Login successful!');
      return data;
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Login failed. Please check your credentials.');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/auth/login');
    toast.success('Logged out successfully');
  };

  const register = async (userData: RegisterData) => {
    try {
      const data = await api.auth.register(userData);
      localStorage.setItem('token', data.access_token);
      setUser(data.user);
      toast.success('Registration successful!');
      return data;
    } catch (error) {
      console.error('Registration failed:', error);
      toast.error('Registration failed. Please try again.');
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};