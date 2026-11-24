import { useState } from 'react';
import { Link } from 'react-router-dom';
import { userRegister } from '../api/endpoints';
import WebcamCapture from '../components/WebcamCapture';
import { UserPlus, CheckCircle, ArrowLeft, Upload } from 'lucide-react';

export default function UserSignUp() {
  const [fullName,     setFullName]     = useState('');
  const [displayName,  setDisplayName]  = useState('');
  const [capturedFile, setCapturedFile] = useState(null);
  const [uploadFile,   setUploadFile]   = useState(null);
  const [inputMode,    setInputMode]    = useState('camera'); // 'camera' | 'upload'
  const [loading,      setLoading]      = useState(false);
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState('');

  const activeFile = inputMode === 'camera' ? capturedFile : uploadFile;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) { setError('Please enter your full name.'); return; }
    if (!activeFile)      { setError('Please capture or upload a face photo.'); return; }

    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await userRegister(fullName.trim(), displayName.trim() || fullName.trim(), activeFile);
      setResult(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (result?.success) {
    return (
      <div className="portal-page">
        <div className="result-screen success-screen">
          <CheckCircle size={72} color="#22c55e" />
          <h2>Welcome, {result.display_name}!</h2>
          <p className="result-msg-big">Your face has been registered successfully.</p>
          <p className="result-sub">You can now sign in anytime using just your face — no password needed.</p>
          <div style={{ display:'flex', gap: 12, marginTop: 24 }}>
            <Link to="/user/signin" className="btn btn-primary">Sign In Now →</Link>
            <Link to="/user"        className="btn btn-ghost">Back to Portal</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="portal-page">
      <div className="portal-form-wrap">
        <Link to="/user" className="back-link"><ArrowLeft size={15}/> Back to Portal</Link>
        <h1 className="portal-form-title"><UserPlus size={28}/> Create Your Account</h1>
        <p className="portal-form-sub">Register your face — takes less than 30 seconds</p>

        <form onSubmit={handleSubmit} className="portal-form">
          {/* Name fields */}
          <div className="form-row">
            <label>
              <span>Full Name <span className="required">*</span></span>
              <input
                type="text" value={fullName} onChange={e => setFullName(e.target.value)}
                placeholder="e.g. Aryan Singh" className="form-input" required
              />
              <span className="form-hint">Used as your unique identity key (stored as Aryan_Singh)</span>
            </label>
            <label>
              <span>Display Name</span>
              <input
                type="text" value={displayName} onChange={e => setDisplayName(e.target.value)}
                placeholder="e.g. Aryan (optional)" className="form-input"
              />
            </label>
          </div>

          {/* Photo input mode toggle */}
          <div className="form-section">
            <div className="section-label">Face Photo <span className="required">*</span></div>
            <div className="tab-row" style={{ maxWidth: 320 }}>
              <button type="button" className={`tab ${inputMode==='camera'?'tab-active':''}`}
                      onClick={() => setInputMode('camera')}>Live Camera</button>
              <button type="button" className={`tab ${inputMode==='upload'?'tab-active':''}`}
                      onClick={() => setInputMode('upload')}><Upload size={14}/> Upload Photo</button>
            </div>

            {inputMode === 'camera' && (
              <WebcamCapture
                label="Capture My Face"
                onCapture={(f) => { setCapturedFile(f); setError(''); }}
                onReset={() => setCapturedFile(null)}
              />
            )}

            {inputMode === 'upload' && (
              <div className="upload-area">
                <label className="dropzone" style={{ minHeight: 160 }}>
                  <input type="file" accept="image/*" hidden
                    onChange={e => { setUploadFile(e.target.files[0]); setError(''); }} />
                  {uploadFile
                    ? <img src={URL.createObjectURL(uploadFile)} alt="preview" className="captured-img" />
                    : <div className="dropzone-hint"><Upload size={36}/><span>Click to select a photo</span></div>}
                </label>
              </div>
            )}

            <p className="form-hint">Use a clear frontal face photo with good lighting. Glasses are okay.</p>
          </div>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" className="btn btn-primary portal-submit-btn" disabled={loading || !activeFile}>
            {loading ? 'Registering...' : <><UserPlus size={18}/> Register My Face</>}
          </button>
        </form>

        <p className="portal-switch-link">
          Already registered? <Link to="/user/signin">Sign in here →</Link>
        </p>
      </div>
    </div>
  );
}
