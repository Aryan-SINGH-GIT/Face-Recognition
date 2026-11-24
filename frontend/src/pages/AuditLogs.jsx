import { useState, useEffect, useCallback } from 'react';
import { getLogs } from '../api/endpoints';
import StatusBadge from '../components/StatusBadge';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';

const PAGE_SIZE = 15;

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchLogs = useCallback(() => {
    setLoading(true);
    getLogs(page, PAGE_SIZE, status)
      .then((r) => {
        setLogs(r.data.logs);
        setTotal(r.data.total);
      })
      .finally(() => setLoading(false));
  }, [page, status]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="content-container">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title">Audit Trail</h1>
          <p className="page-subtitle">{total} verification evaluations logged</p>
        </div>

        <div className="filter-row">
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="select-field"
          >
            <option value="">All Events</option>
            <option value="GRANTED">Granted</option>
            <option value="DENIED">Denied</option>
            <option value="SPOOF">Spoof</option>
          </select>

          <button type="button" className="btn-icon" onClick={fetchLogs} title="Refresh">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-state">
            <p>Loading audit records...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="minimal-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Identity</th>
                  <th>Decision</th>
                  <th>Confidence</th>
                  <th>Liveness</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="font-mono text-muted">
                      {log.timestamp ? log.timestamp.slice(0, 19).replace('T', ' ') : '—'}
                    </td>
                    <td className="font-medium">
                      {log.matched_identity ? log.matched_identity.replace(/_/g, ' ') : <span className="text-dim">Unknown</span>}
                    </td>
                    <td>
                      <StatusBadge status={log.status} />
                    </td>
                    <td className="font-mono">
                      {log.confidence_score != null ? `${log.confidence_score.toFixed(1)}%` : '—'}
                    </td>
                    <td>
                      <span className="text-muted">
                        {log.liveness_passed ? '✓ Live' : '✗ Spoof'}
                      </span>
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={5} className="empty-cell">
                      No logs found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination-bar">
          <button
            type="button"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="btn btn-sm btn-subtle"
          >
            <ChevronLeft size={14} />
            <span>Prev</span>
          </button>
          <span className="page-counter">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="btn btn-sm btn-subtle"
          >
            <span>Next</span>
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
