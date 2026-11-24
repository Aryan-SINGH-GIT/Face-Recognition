export default function StatusBadge({ status }) {
  const map = {
    GRANTED: { dot: 'bg-emerald', text: 'Granted' },
    DENIED:  { dot: 'bg-rose',    text: 'Denied' },
    SPOOF:   { dot: 'bg-amber',   text: 'Spoof' },
    SPOOF_DETECTED: { dot: 'bg-amber', text: 'Spoof' },
    NO_FACE: { dot: 'bg-zinc',    text: 'No Face' },
  };

  const current = map[status] || { dot: 'bg-zinc', text: status };

  return (
    <span className="status-pill">
      <span className={`status-dot ${current.dot}`} />
      <span>{current.text}</span>
    </span>
  );
}
