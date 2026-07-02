import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHistory, fetchHealth } from "../api.js";
import ScoreCard from "../components/ScoreCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function Dashboard() {
  const [reports, setReports] = useState([]);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([fetchHistory(), fetchHealth()])
      .then(([history, healthResponse]) => {
        setReports(history.reports || []);
        setHealth(healthResponse);
      })
      .catch((err) => setError(err.message));
  }, []);

  const stats = useMemo(() => {
    const total = reports.length;
    const passed = reports.reduce((sum, item) => sum + (item.passed || 0), 0);
    const warnings = reports.reduce((sum, item) => sum + (item.warnings || 0), 0);
    const failed = reports.reduce((sum, item) => sum + (item.failed || 0), 0);
    return { total, passed, warnings, failed, latest: reports[0] };
  }, [reports]);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Local-first ECS validation</span>
          <h1>Deployment Readiness Dashboard</h1>
        </div>
        <Link className="primary-action" to="/new">New Check</Link>
      </header>

      {error && <div className="notice error">{error}</div>}

      <section className="metrics-grid">
        <ScoreCard label="Total checks" value={stats.total} />
        <ScoreCard label="Passed checks" value={stats.passed} tone="good" />
        <ScoreCard label="Warning checks" value={stats.warnings} tone="warn" />
        <ScoreCard label="Failed checks" value={stats.failed} tone="bad" />
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Latest Report</h2>
          {health && <span className="muted">API {health.status}</span>}
        </div>
        {stats.latest ? (
          <div className="latest-report">
            <div>
              <strong>{stats.latest.image}</strong>
              <span>{stats.latest.created_at}</span>
            </div>
            <StatusBadge status={stats.latest.final_status} />
            <strong>{stats.latest.score}%</strong>
            <Link to={`/reports/${stats.latest.report_id}`}>Open</Link>
          </div>
        ) : (
          <p className="empty-state">No reports yet.</p>
        )}
      </section>
    </div>
  );
}
