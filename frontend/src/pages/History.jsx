import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHistory } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function History() {
  const [reports, setReports] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHistory()
      .then((data) => setReports(data.reports || []))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Previous validations</span>
          <h1>History</h1>
        </div>
      </header>
      {error && <div className="notice error">{error}</div>}
      <section className="panel table-panel">
        <table>
          <thead>
            <tr>
              <th>Created</th>
              <th>Image</th>
              <th>Mode</th>
              <th>Status</th>
              <th>Score</th>
              <th>Report</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.report_id}>
                <td>{report.created_at}</td>
                <td>{report.image}</td>
                <td>{report.mode}</td>
                <td><StatusBadge status={report.final_status} /></td>
                <td>{report.score}%</td>
                <td><Link to={`/reports/${report.report_id}`}>Open</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
        {reports.length === 0 && <p className="empty-state">No reports yet.</p>}
      </section>
    </div>
  );
}
