import { Link } from 'react-router-dom';
import { ScanFace, UserPlus, Shield, Zap, Eye, Lock } from 'lucide-react';

export default function UserPortal() {
  return (
    <div className="portal-page">
      {/* Hero */}
      <div className="portal-hero">
        <div className="portal-hero-badge">
          <Shield size={16} /> Biometric Access Control
        </div>
        <h1 className="portal-hero-title">
          Your Face is<br />
          <span className="gradient-text">Your Password</span>
        </h1>
        <p className="portal-hero-sub">
          Register once, sign in instantly with just your face.<br />
          No passwords. No cards. Pure biometric security.
        </p>

        <div className="portal-cta">
          <Link to="/user/signup" className="btn btn-primary portal-btn-lg">
            <UserPlus size={20} /> Sign Up — Register My Face
          </Link>
          <Link to="/user/signin" className="btn btn-secondary portal-btn-lg">
            <ScanFace size={20} /> Sign In — Scan My Face
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="portal-features">
        {[
          { icon: <Zap size={22}/>,   title: 'Instant Verification',  desc: 'Under 1 second from photo to access decision using FaceNet embeddings.' },
          { icon: <Eye size={22}/>,   title: 'Liveness Detection',    desc: 'Passive anti-spoofing prevents photo attacks with blur & chrominance analysis.' },
          { icon: <Lock size={22}/>,  title: 'Encrypted Vectors',     desc: '512-D face embeddings stored in Faiss — original images are never saved.' },
          { icon: <Shield size={22}/>, title: 'Full Audit Trail',     desc: 'Every access attempt is logged with timestamp, confidence, and IP in SQLite.' },
        ].map(({ icon, title, desc }) => (
          <div key={title} className="feature-card">
            <div className="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
          </div>
        ))}
      </div>

      {/* Footer nav back to admin */}
      <div className="portal-admin-link">
        <Link to="/" className="text-link">Admin Dashboard →</Link>
      </div>
    </div>
  );
}
