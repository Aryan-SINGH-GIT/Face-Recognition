import { createContext, useContext, useState } from 'react';
import { logoutAdmin } from '../api/endpoints';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('jwt_token'));
  const [role, setRole]   = useState(() => localStorage.getItem('admin_role') || '');

  const isAuthenticated = Boolean(token);

  const saveLogin = (access_token, admin_role) => {
    localStorage.setItem('jwt_token', access_token);
    localStorage.setItem('admin_role', admin_role);
    setToken(access_token);
    setRole(admin_role);
  };

  const logout = async () => {
    try {
      await logoutAdmin();
    } catch (err) {
      // Ignore if session already expired on server
      console.warn("Logout request completed or expired:", err?.message);
    } finally {
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('admin_role');
      setToken(null);
      setRole('');
    }
  };

  return (
    <AuthContext.Provider value={{ token, role, isAuthenticated, saveLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
