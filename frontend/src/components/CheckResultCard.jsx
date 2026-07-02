import StatusBadge from "./StatusBadge.jsx";

export default function CheckResultCard({ check }) {
  return (
    <article className="check-card">
      <div className="check-card-header">
        <div>
          <h3>{check.name}</h3>
          <span className="severity">{check.severity}</span>
        </div>
        <StatusBadge status={check.status} />
      </div>
      <p className="evidence">{check.evidence}</p>
      <p className="recommendation">{check.recommendation}</p>
    </article>
  );
}
