function ProgressBar({ current = 0, total = 0 }) {
  const ratio = total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;

  return (
    <div className="card p-4">
      <div className="flex justify-between text-sm text-slate-600 mb-2">
        <span>Batch Progress</span>
        <span>{current} / {total}</span>
      </div>
      <div className="h-3 w-full rounded-full bg-slate-200 overflow-hidden">
        <div className="h-full rounded-full bg-brand-500 transition-all duration-300" style={{ width: `${ratio}%` }} />
      </div>
    </div>
  );
}

export default ProgressBar;
