import { useState, useEffect } from 'react';
import { getIdentities, deleteIdentity, enrollFace } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { Trash2, Plus, Search, RefreshCw, UserCheck } from 'lucide-react';

export default function Identities() {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Enroll modal / inline form
  const [showEnroll, setShowEnroll] = useState(false);
  const [enrollName, setEnrollName] = useState('');
  const [enrollFile, setEnrollFile] = useState(null);
  const [enrolling, setEnrolling] = useState(false);

  const fetchIdentities = () => {
    setLoading(true);
    getIdentities()
      .then((r) => setData(r.data))
      .catch(() => setError('Failed to load identities'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchIdentities();
  }, []);

  const handleDelete = async (identity) => {
    if (!window.confirm(`Delete "${identity}" from vector database?`)) return;
    setError('');
    setSuccess('');
    try {
      await deleteIdentity(identity);
      setSuccess(`Deleted ${identity}`);
      fetchIdentities();
    } catch (e) {
      setError(e.response?.data?.detail || 'Delete failed');
    }
  };

  const handleEnroll = async (e) => {
    e.preventDefault();
    if (!enrollName.trim() || !enrollFile) return;
    setEnrolling(true);
    setError('');
    setSuccess('');

    try {
      await enrollFace(enrollName.trim(), enrollFile);
      setSuccess(`Successfully enrolled ${enrollName.trim()}`);
      setEnrollName('');
      setEnrollFile(null);
      setShowEnroll(false);
      fetchIdentities();
    } catch (e) {
      setError(e.response?.data?.detail || 'Enrollment failed');
    } finally {
      setEnrolling(false);
    }
  };

  const filtered = (data?.unique_identities || []).filter((id) =>
    id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="content-container">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title">Enrolled Identities</h1>
          <p className="page-subtitle">
            {data ? `${data.unique_count} people • ${data.total_count} vector embeddings` : 'Loading...'}
          </p>
        </div>

        {isAuthenticated && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => setShowEnroll((s) => !s)}
          >
            <Plus size={14} />
            <span>{showEnroll ? 'Close Form' : 'Enroll Person'}</span>
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Admin Enroll Form */}
      {showEnroll && isAuthenticated && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 className="card-title">Enroll New Identity</h3>
          <form onSubmit={handleEnroll} className="inline-form">
            <input
              type="text"
              placeholder="Identity Name (e.g. John_Doe)"
              value={enrollName}
              onChange={(e) => setEnrollName(e.target.value)}
              className="input-field"
              required
            />
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setEnrollFile(e.target.files[0])}
              className="input-field"
              required
            />
            <button type="submit" className="btn btn-primary" disabled={enrolling}>
              {enrolling ? 'Enrolling...' : 'Save to Faiss'}
            </button>
          </form>
        </div>
      )}

      {/* Search Bar */}
      <div className="search-wrap">
        <Search size={15} className="search-icon" />
        <input
          type="text"
          placeholder="Filter identities..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
      </div>

      {/* List */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-state">
            <p>Loading database...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="minimal-table">
              <thead>
                <tr>
                  <th>Identity</th>
                  <th>Vector Dimension</th>
                  <th>Status</th>
                  {isAuthenticated && <th style={{ textAlign: 'right' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.map((id) => (
                  <tr key={id}>
                    <td>
                      <div className="identity-cell">
                        <div className="avatar-circle">{id[0].toUpperCase()}</div>
                        <span className="font-medium">{id.replace(/_/g, ' ')}</span>
                      </div>
                    </td>
                    <td className="font-mono text-muted">512-D L2</td>
                    <td>
                      <span className="status-pill">
                        <span className="status-dot bg-emerald" />
                        <span>Enrolled</span>
                      </span>
                    </td>
                    {isAuthenticated && (
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn-icon text-rose"
                          title="Delete Identity"
                          onClick={() => handleDelete(id)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={isAuthenticated ? 4 : 3} className="empty-cell">
                      No identities matching "{search}"
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
