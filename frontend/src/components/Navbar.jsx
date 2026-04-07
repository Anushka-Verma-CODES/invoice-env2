function Navbar() {
  return (
    <header className="bg-brand-700 text-white">
      <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Invoice & Receipt Processing Platform</h1>
          <p className="text-sm text-blue-100">OpenEnv + AI Agents + Analytics Dashboard</p>
        </div>
        <div className="rounded-full bg-white/15 px-3 py-1 text-xs">Hackathon Edition</div>
      </div>
    </header>
  );
}

export default Navbar;
