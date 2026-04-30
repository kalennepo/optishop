import { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../api/client';

const AuthContext = createContext(null);

function decodeToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(() => {
    const t = localStorage.getItem('token');
    return t ? decodeToken(t) : null;
  });

  const login = async (email, password) => {
    const res = await apiLogin(email, password);
    const { access_token } = res.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    const decoded = decodeToken(access_token);
    setUser(decoded);
    return decoded;
  };

  const register = async (email, password, role) => {
    await apiRegister(email, password, role);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const role = user?.role ?? null;

  return (
    <AuthContext.Provider value={{ token, user, role, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
