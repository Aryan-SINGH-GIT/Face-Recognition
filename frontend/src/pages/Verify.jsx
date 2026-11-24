import { useState } from 'react';
import { verifyFace } from '../api/endpoints';
import StatusBadge from '../components/StatusBadge';
import WebcamCapture from '../components/WebcamCapture';
import { Camera, Upload, ScanFace, RefreshCw } from 'lucide-react';

export default function Verify() {
  const [mode, setMode] = useState('upload'); // 'upload' | 'camera'
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ── File upload ─────────────────────────────────────────────────────────────
  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError('');
  };

  // ── Submit ──────────────────────────────────────────────────────────────────
  const handleVerify = async (fileToVerify = file) => {
    const target = fileToVerify || file;
    if (!target) {
      setError('Please select or capture an image first.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await verifyFace(target);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed. Check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="page">
      <h1 className="page-title">Face Verification</h1>
      <p className="page-sub">Upload or capture a face image to verify identity against the vector store</p>

      <div className="verify-layout">
        {/* Left: Input */}
        <div className="card verify-input">
          <div className="tab-row">
            <button
              type="button"
              className={`tab ${mode === 'upload' ? 'tab-active' : ''}`}
              onClick={() => {
                setMode('upload');
                reset();
              }}
            >
              <Upload size={16} /> Upload Photo
            </button>
            <button
              type="button"
              className={`tab ${mode === 'camera' ? 'tab-active' : ''}`}
              onClick={() => {
                setMode('camera');
                reset();
              }}
            >
              <Camera size={16} /> Live Camera
            </button>
          </div>

          {mode === 'upload' && (
            <label className="dropzone">
              <input type="file" accept="image/*" onChange={handleFile} hidden />
              {preview ? (
                <img src={preview} alt="preview" className="preview-img" />
              ) : (
                <div className="dropzone-hint">
                  <Upload size={40} />
                  <span>Click or drag an image here</span>
                </div>
              )}
            </label>
          )}

          {mode === 'camera' && (
            <WebcamCapture
              label="Capture & Verify"
              autoStart={true}
              onCapture={(capturedFile) => {
                setFile(capturedFile);
                handleVerify(capturedFile);
              }}
              onReset={reset}
            />
          )}

          {mode === 'upload' && (
            <div className="verify-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => handleVerify(file)}
                disabled={loading || !file}
              >
                {loading ? (
                  <>
                    <RefreshCw size={16} className="spin" /> Verifying...
                  </>
                ) : (
                  <>
                    <ScanFace size={16} /> Verify Face
                  </>
                )}
              </button>
              <button type="button" className="btn btn-ghost" onClick={reset}>
                Reset
              </button>
            </div>
          )}

          {error && <div className="error-box" style={{ marginTop: 14 }}>{error}</div>}
        </div>

        {/* Right: Result */}
        <div className="card verify-result">
          <h2 className="card-title">Verification Outcome</h2>
          {!result && (
            <div className="result-placeholder">
              <ScanFace size={60} color="#6366f1" opacity={0.3} />
              <p>Biometric results will appear here once verified</p>
            </div>
          )}
          {result && (
            <div className={`result-box ${result.status === 'GRANTED' ? 'result-granted' : 'result-denied'}`}>
              <div className="result-status">
                <StatusBadge status={result.status} />
              </div>
              <div className="result-identity">{result.identity || 'Unrecognized Person'}</div>
              <div className="result-meta">
                <span>
                  Confidence: <strong>{result.confidence != null ? `${result.confidence}%` : '—'}</strong>
                </span>
                <span>
                  L2 Distance: <strong>{result.distance != null ? result.distance.toFixed(4) : '—'}</strong>
                </span>
                <span>
                  Liveness: <strong>{result.is_live ? '✓ Live Face' : '✗ Spoof'}</strong>
                </span>
              </div>
              {result.liveness_details && (
                <div className="liveness-detail">
                  <div>Blur Variance: {result.liveness_details.blur_variance?.toFixed(1)}</div>
                  <div>Chrominance Std: {result.liveness_details.chroma_std?.toFixed(2)}</div>
                  <div>Moire Ratio: {result.liveness_details.moire_ratio?.toFixed(3)}</div>
                </div>
              )}
              {result.message && <div className="result-msg">{result.message}</div>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
