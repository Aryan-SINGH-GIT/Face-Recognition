import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ScanFace, LayoutDashboard, Users, ScrollText, BarChart2, LogOut, Lock } from 'lucide-react';

export default function Navbar() {
  const { isAuthenticated, logout, role } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Brand */}
        <NavLink to="/" className="navbar-brand">
          <span className="brand-dot" />
          <span className="brand-name">FaceGuard</span>
          <span className="brand-badge">Biometric</span>
        </NavLink>

        {/* Admin Navigation Links - ONLY VISIBLE WHEN AUTHENTICATED AS ADMIN */}
        {isAuthenticated && (
          <nav className="navbar-links">
            <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <ScanFace size={15} />
              <span>Face Terminal</span>
            </NavLink>
            <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <LayoutDashboard size={15} />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/identities" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Users size={15} />
              <span>Identities</span>
            </NavLink>
            <NavLink to="/logs" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <ScrollText size={15} />
              <span>Logs</span>
            </NavLink>
            <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <BarChart2 size={15} />
              <span>Analytics</span>
            </NavLink>
          </nav>
        )}

        {/* Right side auth */}
        <div className="navbar-actions">
          {isAuthenticated ? (
            <div className="auth-group">
              <span className="role-tag">{role}</span>
              <button onClick={handleLogout} className="btn-icon" title="Logout">
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <NavLink to="/login" className="login-link">
              <Lock size={12} style={{ display: 'inline', marginRight: 4 }} />
              <span>Admin Login</span>
            </NavLink>
          )}
        </div>
      </div>
    </header>
  );
}
