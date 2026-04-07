function Badge({ value, positive = true }) {
  return (
    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${positive ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
      {value}
    </span>
  );
}

function AgentOutput({ result }) {
  if (!result) {
    return (
      <section className="card p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-2">Agent Output</h2>
        <p className="text-slate-500">Run next step or full agent to see predictions.</p>
      </section>
    );
  }

  const action = result.action || {};
  const extracted = action.extracted_fields || {};

  return (
    <section className="card p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Agent Output</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="text-xs text-slate-500 mb-1">Extracted Vendor</p>
          <p className="font-medium text-slate-900">{extracted.vendor_name || "-"}</p>
        </div>
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="text-xs text-slate-500 mb-1">Extracted Date</p>
          <p className="font-medium text-slate-900">{extracted.invoice_date || "-"}</p>
        </div>
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="text-xs text-slate-500 mb-1">Category</p>
          <p className="font-medium text-slate-900">{action.category || "-"}</p>
        </div>
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="text-xs text-slate-500 mb-1">Anomaly Flag</p>
          <Badge value={String(action.anomaly_flag)} positive={!action.anomaly_flag} />
        </div>
      </div>
    </section>
  );
}

export default AgentOutput;
