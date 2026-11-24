import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { userLogin } from '../api/endpoints';
import WebcamCapture from '../components/WebcamCapture';
import { ScanFace, CheckCircle, XCircle, ArrowLeft, Upload, RefreshCw, LogIn } from 'lucide-react';

export default function UserSignIn() {
  const [capturedFile, setCapturedFile] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [inputMode, setInputMode] = useState('camera');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const activeFile = inputMode === 'camera' ? capturedFile : uploadFile;

  // Execute verification against backend
  const executeLogin = useCallback(async (fileToVerify) => {
    if (!fileToVerify) {
      setError('Please provide a face photo first.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await userLogin(fileToVerify);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification request failed. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleCapture = (file) => {
    setCapturedFile(file);
    setError('');
    // Automatically verify immediately upon capture for seamless 1-click UX
    executeLogin(file);
  };

  const handleReset = () => {
    setCapturedFile(null);
    setUploadFile(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="portal-page">
      <div className="portal-form-wrap" style={{ maxWidth: 580 }}>
        <Link to="/user" className="back-link">
          <ArrowLeft size={15} /> Back to Portal
        </Link>
        <h1 className="portal-form-title">
          <ScanFace size={28} /> Face Sign In
        </h1>
        <p className="portal-form-sub">Look at your webcam — we'll authenticate your identity</p>

        {/* Input Mode Selector */}
        <div className="tab-row" style={{ maxWidth: 320, marginBottom: 16 }}>
          <button
            type="button"
            className={`tab ${inputMode === 'camera' ? 'tab-active' : ''}`}
            onClick={() => {
              setInputMode('camera');
              handleReset();
            }}
          >
            Live Camera
          </button>
          <button
            type="button"
            className={`tab ${inputMode === 'upload' ? 'tab-active' : ''}`}
            onClick={() => {
              setInputMode('upload');
              handleReset();
            }}
          >
            <Upload size={14} /> Upload Photo
          </button>
        </div>

        {/* Loading Spinner Indicator */}
        {loading && (
          <div className="card page-center" style={{ flexDirection: 'column', gap: 12 }}>
            <RefreshCw size={36} className="spin" color="#6366f1" />
            <p style={{ color: '#fff', fontWeight: 600 }}>Analyzing face & verifying identity...</p>
            <p style={{ fontSize: 12, color: 'var(--text-sub)' }}>MTCNN face detection $\rightarrow$ FaceNet 512-D embedding $\rightarrow$ Faiss search</p>
          </div>
        )}

        {/* Verification Inputs (Hidden while loading or when result is shown) */}
        {!loading && !result && (
          <>
            {inputMode === 'camera' && (
              <WebcamCapture
                label="Scan My Face"
                autoStart={true}
                onCapture={handleCapture}
                onReset={() => {
                  setCapturedFile(null);
                  setResult(null);
                }}
              />
            )}

            {inputMode === 'upload' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <label className="dropzone" style={{ minHeight: 180 }}>
                  <input
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={(e) => {
                      const f = e.target.files[0];
                      if (f) {
                        setUploadFile(f);
                        setError('');
                      }
                    }}
                  />
                  {uploadFile ? (
                    <img
                      src={URL.createObjectURL(uploadFile)}
                      alt="preview"
                      className="captured-img"
                      style={{ maxHeight: 220 }}
                    />
                  ) : (
                    <div className="dropzone-hint">
                      <Upload size={36} />
                      <span>Click or drag a face photo here</span>
                    </div>
                  )}
                </label>

                <button
                  type="button"
                  className="btn btn-primary portal-submit-btn"
                  onClick={() => executeLogin(uploadFile)}
                  disabled={!uploadFile}
                >
                  <ScanFace size={18} /> Verify & Sign In
                </button>
              </div>
            )}

            {error && <div className="error-box" style={{ marginTop: 14 }}>{error}</div>}
          </>
        )}

        {/* Verification Results Screen */}
        {!loading && result && (
          <div className={`signin-result ${result.granted ? 'result-granted' : 'result-denied'}`}>
            {result.granted ? (
              <CheckCircle size={68} color="#22c55e" />
            ) : (
              <XCircle size={68} color="#ef4444" />
            )}

            <h2 className="result-heading">
              {result.granted ? 'Access Granted!' : 'Access Denied'}
            </h2>

            {result.granted && (
              <div className="user-welcome-box">
                <div className="user-avatar-lg">
                  {(result.display_name || result.full_name || '?')[0].toUpperCase()}
                </div>
                <div>
                  <div className="welcome-name">
                    Welcome, <strong>{result.display_name || result.full_name}</strong>!
                  </div>
                  <div className="welcome-meta">
                    <span>
                      Confidence: <strong>{result.confidence != null ? `${result.confidence.toFixed(1)}%` : '—'}</strong>
                    </span>
                    {result.total_access != null && (
                      <span>
                        Visits: <strong>{result.total_access}</strong>
                      </span>
                    )}
                    <span>
                      Liveness: <strong>{result.is_live ? '✓ Live Face' : '✗ Spoof'}</strong>
                    </span>
                  </div>
                </div>
              </div>
            )}

            {!result.granted && (
              <p className="denied-msg" style={{ margin: '8px 0', color: 'var(--text-sub)' }}>
                {result.message || 'Face not recognized in the database.'}
              </p>
            )}

            <div style={{ display: 'flex', gap: 12, marginTop: 18 }}>
              <button type="button" className="btn btn-primary" onClick={handleReset}>
                <RefreshCw size={14} /> Try Another Scan
              </button>
              {!result.granted && (
                <Link to="/user/signup" className="btn btn-secondary">
                  Create New Account →
                </Link>
              )}
            </div>
          </div>
        )}

        <p className="portal-switch-link" style={{ marginTop: 24 }}>
          New user? <Link to="/user/signup">Register your face →</Link>
        </p>
      </div>
    </div>
  );
}
