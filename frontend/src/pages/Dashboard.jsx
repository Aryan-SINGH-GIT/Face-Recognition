import { useState, useEffect } from 'react';
import { getHealth, getConfig, getSummary, setSpoofDetection } from '../api/endpoints';
import { CheckCircle2, XCircle, ShieldCheck, ShieldAlert, ToggleLeft, ToggleRight, Loader2 } from 'lucide-react';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [config, setConfig] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [togglingSpoof, setTogglingSpoof] = useState(false);
  const [toggleMsg, setToggleMsg] = useState('');

  const loadData = () => {
    return Promise.all([getHealth(), getConfig(), getSummary()])
      .then(([h, c, s]) => {
        setHealth(h.data);
        setConfig(c.data);
        setSummary(s.data);
      });
  };

  useEffect(() => {
    loadData().finally(() => setLoading(false));
  }, []);

  const handleToggleSpoof = async () => {
    if (!config) return;
    const nextState = !config.liveness_enabled;
    setTogglingSpoof(true);
    setToggleMsg('');
    try {
      const res = await setSpoofDetection(nextState);
      setConfig((prev) => ({ ...prev, liveness_enabled: res.data.liveness_enabled }));
      setToggleMsg(res.data.message);
      setTimeout(() => setToggleMsg(''), 4000);
    } catch (err) {
      setToggleMsg(err.response?.data?.detail || 'Failed to update spoof detection setting');
    } finally {
      setTogglingSpoof(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state" style={{ minHeight: '50vh' }}>
        <p>Loading dashboard metrics...</p>
      </div>
    );
  }

  const isOnline = health?.status === 'ok';
  const isSpoofActive = Boolean(config?.liveness_enabled);

  return (
    <div className="content-container">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title">System Overview</h1>
          <p className="page-subtitle">Real-time biometric engine metrics and vector store status</p>
        </div>
        <div className={`status-tag ${isOnline ? 'online' : 'offline'}`}>
          <span className="dot" />
          <span>{isOnline ? 'Engine Online' : 'Engine Offline'}</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Total Verifications</span>
          <span className="metric-value">{summary?.total_verifications ?? 0}</span>
          <span className="metric-caption">Lifetime access evaluations</span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Pass Rate</span>
          <span className="metric-value">{summary?.pass_rate_percentage ?? 0}%</span>
          <span className="metric-caption">
            {summary?.granted_count ?? 0} granted / {summary?.denied_count ?? 0} denied
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Enrolled Identities</span>
          <span className="metric-value">{summary?.enrolled_identities_count ?? 0}</span>
          <span className="metric-caption">{health?.total_embeddings ?? 0} total vector embeddings</span>
        </div>

        <div className={`metric-card ${!isSpoofActive ? 'metric-card-warning' : ''}`} style={{ position: 'relative' }}>
          <span className="metric-label">Anti-Spoofing</span>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
            <span className="metric-value" style={{ color: isSpoofActive ? 'var(--emerald)' : 'var(--rose)' }}>
              {isSpoofActive ? 'Active' : 'Disabled'}
            </span>
            <button
              onClick={handleToggleSpoof}
              disabled={togglingSpoof}
              title={isSpoofActive ? 'Click to Disable Anti-Spoofing' : 'Click to Enable Anti-Spoofing'}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: togglingSpoof ? 'not-allowed' : 'pointer',
                color: isSpoofActive ? 'var(--emerald)' : 'var(--text-dim)',
                display: 'flex',
                alignItems: 'center',
                padding: 4
              }}
            >
              {togglingSpoof ? (
                <Loader2 size={24} className="animate-spin" />
              ) : isSpoofActive ? (
                <ToggleRight size={30} style={{ color: 'var(--emerald)' }} />
              ) : (
                <ToggleLeft size={30} style={{ color: 'var(--rose)' }} />
              )}
            </button>
          </div>
          <span className="metric-caption">
            {isSpoofActive ? 'Laplacian + Chrominance enabled' : 'Bypassed by administrator'}
          </span>
        </div>
      </div>

      {toggleMsg && (
        <div style={{
          marginTop: 16,
          padding: '10px 16px',
          borderRadius: 8,
          background: isSpoofActive ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
          border: `1px solid ${isSpoofActive ? 'var(--emerald)' : 'var(--rose)'}`,
          color: isSpoofActive ? 'var(--emerald)' : 'var(--rose)',
          fontSize: 13,
          fontWeight: 500
        }}>
          {toggleMsg}
        </div>
      )}

      {/* Two Column Section */}
      <div className="grid-2col" style={{ marginTop: 24 }}>
        {/* ML Performance */}
        <div className="card">
          <h2 className="card-title">Biometric Benchmark (TAR @ FAR)</h2>
          <div className="key-value-list">
            <div className="kv-item">
              <span className="kv-key">ROC AUC Score</span>
              <span className="kv-val font-mono">0.9860</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">TAR @ FAR = 1%</span>
              <span className="kv-val font-mono">95.07%</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">TAR @ FAR = 10%</span>
              <span className="kv-val font-mono">97.54%</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">Feature Extractor</span>
              <span className="kv-val">InceptionResnetV1 (vggface2)</span>
            </div>
          </div>
        </div>

        {/* Model Configuration & Security Controls */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 className="card-title">Engine Configuration & Controls</h2>
          </div>
          <div className="key-value-list">
            <div className="kv-item">
              <span className="kv-key">Embedding Dimension</span>
              <span className="kv-val font-mono">512-D</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">L2 Threshold</span>
              <span className="kv-val font-mono">{config?.threshold ?? 1.2}</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">Inference Hardware</span>
              <span className="kv-val">{config?.device?.toUpperCase() ?? 'CPU'}</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">Vector Database</span>
              <span className="kv-val">Faiss IndexFlatL2</span>
            </div>
            <div className="kv-item">
              <span className="kv-key">Anti-Spoofing Filter</span>
              <span className="kv-val" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {isSpoofActive ? (
                  <>
                    <ShieldCheck size={15} style={{ color: 'var(--emerald)' }} />
                    <span style={{ color: 'var(--emerald)', fontWeight: 600 }}>Enabled</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert size={15} style={{ color: 'var(--rose)' }} />
                    <span style={{ color: 'var(--rose)', fontWeight: 600 }}>Disabled (Admin override)</span>
                  </>
                )}
              </span>
            </div>
          </div>

          <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>Admin Anti-Spoofing Control</p>
                <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {isSpoofActive
                    ? 'Currently blocking paper photos, phone screens, and replay attacks.'
                    : 'Spoof checks disabled. Allows testing raw photos and simulated inputs.'}
                </p>
              </div>
              <button
                type="button"
                onClick={handleToggleSpoof}
                disabled={togglingSpoof}
                className="btn btn-secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  borderColor: isSpoofActive ? 'var(--rose)' : 'var(--emerald)',
                  color: isSpoofActive ? 'var(--rose)' : 'var(--emerald)',
                  whiteSpace: 'nowrap'
                }}
              >
                {togglingSpoof ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    <span>Updating...</span>
                  </>
                ) : isSpoofActive ? (
                  <>
                    <ShieldAlert size={14} />
                    <span>Disable Spoof Detection</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck size={14} />
                    <span>Enable Spoof Detection</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

