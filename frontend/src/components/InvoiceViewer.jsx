function InvoiceViewer({ observation }) {
  if (!observation) {
    return (
      <section className="card p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-2">Invoice Viewer</h2>
        <p className="text-slate-500">Reset environment to load an invoice.</p>
      </section>
    );
  }

  const rawText = observation.metadata?.raw_text || "No invoice text available.";

  return (
    <section className="card p-6">
      <h2 className="text-lg font-semibold text-slate-900 mb-4">Invoice Viewer</h2>
      <div className="space-y-3">
        <pre className="whitespace-pre-wrap text-sm bg-slate-50 rounded-xl p-4 border border-slate-100">{rawText}</pre>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-100 p-3">
            <p className="text-xs text-slate-500">Vendor Name</p>
            <p className="font-medium text-slate-900">{observation.vendor_name}</p>
          </div>
          <div className="rounded-xl border border-slate-100 p-3">
            <p className="text-xs text-slate-500">Invoice Date</p>
            <p className="font-medium text-slate-900">{observation.invoice_date}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default InvoiceViewer;
