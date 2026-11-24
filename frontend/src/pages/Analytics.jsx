import { useState, useEffect } from 'react';
import { getSummary } from '../api/endpoints';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { RefreshCw } from 'lucide-react';

const COLORS = {
  GRANTED: '#22c55e',
  DENIED:  '#ef4444',
  SPOOF:   '#f59e0b',
};

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSummary = () => {
    setLoading(true);
    getSummary()
      .then((r) => setSummary(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="loading-state" style={{ minHeight: '50vh' }}>
        <p>Loading analytics...</p>
      </div>
    );
  }

  const pieData = [
    { name: 'Granted', value: summary?.granted_count || 0 },
    { name: 'Denied',  value: summary?.denied_count  || 0 },
    { name: 'Spoof',   value: summary?.spoof_detected_count || 0 },
  ].filter((d) => d.value > 0);

  const barData = [
    { metric: 'AUC',          value: 0.986,  fill: '#3b82f6' },
    { metric: 'TAR@FAR 1%',   value: 0.9507, fill: '#10b981' },
    { metric: 'TAR@FAR 10%',  value: 0.9754, fill: '#6366f1' },
    { metric: 'Pass Rate',    value: (summary?.pass_rate_percentage || 0) / 100, fill: '#f59e0b' },
  ];

  return (
    <div className="content-container">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="page-title">Biometric Analytics</h1>
          <p className="page-subtitle">Access decision distribution and ML evaluation metrics</p>
        </div>
        <button type="button" className="btn-icon" onClick={fetchSummary} title="Refresh">
          <RefreshCw size={14} />
        </button>
      </div>

      <div className="grid-2col">
        {/* Decision Breakdown */}
        <div className="card">
          <h2 className="card-title">Access Decisions</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={50}
                  stroke="#121215"
                  strokeWidth={2}
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={COLORS[entry.name.toUpperCase()] || '#71717a'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fafafa',
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="loading-state" style={{ height: 240 }}>
              <p>No verification data recorded yet</p>
            </div>
          )}
        </div>

        {/* Model Accuracy Benchmark */}
        <div className="card">
          <h2 className="card-title">Model Accuracy Benchmarks</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="metric" tick={{ fontSize: 11, fill: '#a1a1aa' }} />
              <YAxis domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fill: '#71717a', fontSize: 11 }} />
              <Tooltip
                formatter={(v) => `${(v * 100).toFixed(2)}%`}
                contentStyle={{
                  backgroundColor: '#18181b',
                  borderColor: '#27272a',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#fafafa',
                }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
