const statusClass = {
  PASS: "badge pass",
  WARN: "badge warn",
  FAIL: "badge fail",
  READY: "badge ready",
  READY_WITH_WARNINGS: "badge ready-warning",
  NOT_READY: "badge not-ready"
};

export default function StatusBadge({ status }) {
  return <span className={statusClass[status] || "badge"}>{status}</span>;
}
