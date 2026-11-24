import { useState, useCallback } from 'react';
import { userLogin, userRegister } from '../api/endpoints';
import WebcamCapture from '../components/WebcamCapture';
import StatusBadge from '../components/StatusBadge';
import { ScanFace, UserPlus, Upload, CheckCircle2, XCircle, RefreshCw, ArrowRight } from 'lucide-react';

export default function FaceAccess({ initialTab = 'signin' }) {
  const [tab, setTab] = useState(initialTab); // 'signin' | 'register'
  const [inputMode, setInputMode] = useState('camera'); // 'camera' | 'upload'
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Registration state
  const [fullName, setFullName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [regFile, setRegFile] = useState(null);

  // Sign In handler
  const handleSignIn = useCallback(async (fileToVerify) => {
    if (!fileToVerify) {
      setError('Please provide a face image to verify.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await userLogin(fileToVerify);
      setResult({ type: 'signin', data: res.data });
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed. Backend may be offline.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Registration handler
  const handleRegister = useCallback(async (e) => {
    if (e) e.preventDefault();
    if (!fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }
    if (!regFile) {
      setError('Please capture or upload a face photo.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await userRegister(fullName.trim(), displayName.trim() || fullName.trim(), regFile);
      setResult({ type: 'register', data: res.data });
      setFullName('');
      setDisplayName('');
      setRegFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  }, [fullName, displayName, regFile]);

  const handleReset = () => {
    setResult(null);
    setError('');
    setRegFile(null);
  };

  return (
    <div className="center-container">
      <div className="terminal-card">
        {/* Minimal Tab Switcher */}
        <div className="tab-pill-group">
          <button
            type="button"
            className={`tab-pill ${tab === 'signin' ? 'active' : ''}`}
            onClick={() => { setTab('signin'); handleReset(); }}
          >
            <ScanFace size={15} />
            <span>Face Sign In</span>
          </button>
          <button
            type="button"
            className={`tab-pill ${tab === 'register' ? 'active' : ''}`}
            onClick={() => { setTab('register'); handleReset(); }}
          >
            <UserPlus size={15} />
            <span>Register Face</span>
          </button>
        </div>

        {/* Subtitle / Mode selector */}
        <div className="terminal-header">
          <p className="terminal-desc">
            {tab === 'signin'
              ? 'Scan your face to verify identity and gain access'
              : 'Enrolls your 512-D biometric embedding into the vector store'}
          </p>

          <div className="input-toggle">
            <button
              type="button"
              className={`toggle-btn ${inputMode === 'camera' ? 'active' : ''}`}
              onClick={() => { setInputMode('camera'); handleReset(); }}
            >
              Camera
            </button>
            <button
              type="button"
              className={`toggle-btn ${inputMode === 'upload' ? 'active' : ''}`}
              onClick={() => { setInputMode('upload'); handleReset(); }}
            >
              Upload
            </button>
          </div>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="loading-state">
            <RefreshCw size={24} className="spin text-primary" />
            <p>Processing neural embedding...</p>
          </div>
        )}

        {/* SIGN IN VIEW */}
        {!loading && tab === 'signin' && (
          <>
            {!result && (
              <>
                {inputMode === 'camera' && (
                  <WebcamCapture
                    label="Scan Face"
                    autoStart={true}
                    onCapture={(file) => handleSignIn(file)}
                    onReset={handleReset}
                  />
                )}

                {inputMode === 'upload' && (
                  <div className="upload-box">
                    <label className="file-dropzone">
                      <input
                        type="file"
                        accept="image/*"
                        hidden
                        onChange={(e) => {
                          const f = e.target.files[0];
                          if (f) handleSignIn(f);
                        }}
                      />
                      <Upload size={24} className="text-muted" />
                      <span>Click to select face photo</span>
                    </label>
                  </div>
                )}
              </>
            )}

            {/* Verification Result */}
            {result?.type === 'signin' && (
              <div className={`result-card ${result.data.granted ? 'granted' : 'denied'}`}>
                <div className="result-header">
                  {result.data.granted ? (
                    <CheckCircle2 size={24} className="text-emerald" />
                  ) : (
                    <XCircle size={24} className="text-rose" />
                  )}
                  <div>
                    <h3 className="result-title">
                      {result.data.granted
                        ? `Welcome, ${result.data.display_name || result.data.full_name}`
                        : 'Access Denied'}
                    </h3>
                    <p className="result-detail">
                      {result.data.granted
                        ? `Confidence: ${result.data.confidence != null ? result.data.confidence.toFixed(1) : '100'}% • Live Face Verified`
                        : (result.data.message || 'Face does not match any enrolled identity')}
                    </p>
                  </div>
                </div>

                <div className="result-actions">
                  <button type="button" className="btn btn-primary btn-sm" onClick={handleReset}>
                    Scan Again
                  </button>
                  {!result.data.granted && (
                    <button
                      type="button"
                      className="btn btn-subtle btn-sm"
                      onClick={() => { setTab('register'); handleReset(); }}
                    >
                      <span>Register New Face</span>
                      <ArrowRight size={13} />
                    </button>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {/* REGISTER VIEW */}
        {!loading && tab === 'register' && (
          <form onSubmit={handleRegister} className="register-form">
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                placeholder="e.g. Aryan Singh"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-field"
                required
              />
            </div>

            <div className="form-group">
              <label>Face Capture</label>
              {inputMode === 'camera' && (
                <WebcamCapture
                  label="Capture Face"
                  autoStart={true}
                  onCapture={(file) => setRegFile(file)}
                  onReset={() => setRegFile(null)}
                />
              )}

              {inputMode === 'upload' && (
                <label className="file-dropzone">
                  <input
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={(e) => setRegFile(e.target.files[0])}
                  />
                  <Upload size={20} className="text-muted" />
                  <span>{regFile ? regFile.name : 'Choose facial image'}</span>
                </label>
              )}
            </div>

            {result?.type === 'register' && (
              <div className="result-card granted">
                <CheckCircle2 size={20} className="text-emerald" />
                <div style={{ flex: 1 }}>
                  <p className="result-title">Enrolled successfully</p>
                  <p className="result-detail">{result.data.message}</p>
                </div>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => { setTab('signin'); handleReset(); }}
                >
                  Sign In Now
                </button>
              </div>
            )}

            {!result && (
              <button
                type="submit"
                className="btn btn-primary btn-block"
                disabled={!fullName.trim() || !regFile}
              >
                Enroll Identity
              </button>
            )}
          </form>
        )}

        {/* Error message */}
        {error && (
          <div className="alert alert-error" style={{ marginTop: 14 }}>
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
}
