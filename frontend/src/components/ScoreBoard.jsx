function ScoreCard({ title, value }) {
  return (
    <div className="rounded-xl border border-slate-100 p-4 bg-slate-50">
      <p className="text-xs text-slate-500">{title}</p>
      <p className="text-2xl font-semibold text-slate-900 mt-1">{value}</p>
    </div>
  );
}

function ScoreBoard({ reward }) {
  const details = reward?.details || {};

  return (
    <section className="card p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Score Board</h2>
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        <ScoreCard title="Extraction" value={(details.extraction ?? 0).toFixed(3)} />
        <ScoreCard title="Category" value={(details.category ?? 0).toFixed(3)} />
        <ScoreCard title="Anomaly" value={(details.anomaly ?? 0).toFixed(3)} />
        <ScoreCard title="Total" value={(reward?.score ?? 0).toFixed(3)} />
      </div>
    </section>
  );
}

export default ScoreBoard;
