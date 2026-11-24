import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import FaceAccess from './pages/FaceAccess';
import Dashboard from './pages/Dashboard';
import Identities from './pages/Identities';
import AuditLogs from './pages/AuditLogs';
import Analytics from './pages/Analytics';
import Login from './pages/Login';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Admin Login Screen */}
          <Route path="/login" element={<Login />} />

          {/* Main App Layout with Top Navigation */}
          <Route
            path="/*"
            element={
              <div className="app-layout">
                <Navbar />
                <main className="main-viewport">
                  <Routes>
                    {/* Primary Face Access Terminal (Public) */}
                    <Route path="/" element={<FaceAccess initialTab="signin" />} />
                    <Route path="/scan" element={<FaceAccess initialTab="signin" />} />
                    <Route path="/verify" element={<FaceAccess initialTab="signin" />} />

                    {/* Backward-compatible User Portal URLs (Public) */}
                    <Route path="/user" element={<FaceAccess initialTab="signin" />} />
                    <Route path="/user/signin" element={<FaceAccess initialTab="signin" />} />
                    <Route path="/user/signup" element={<FaceAccess initialTab="register" />} />

                    {/* Protected Admin Management & Analytics */}
                    <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                    <Route path="/identities" element={<PrivateRoute><Identities /></PrivateRoute>} />
                    <Route path="/logs" element={<PrivateRoute><AuditLogs /></PrivateRoute>} />
                    <Route path="/analytics" element={<PrivateRoute><Analytics /></PrivateRoute>} />

                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </main>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
