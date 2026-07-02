import { Download } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchReport } from "../api.js";
import CheckResultCard from "../components/CheckResultCard.jsx";
import ScoreCard from "../components/ScoreCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

function downloadFile(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function reportToMarkdown(report) {
  const checkLines = report.checks
    .map((check) => `### ${check.name}\n\n- Status: **${check.status}**\n- Severity: **${check.severity}**\n- Evidence: ${check.evidence}\n- Recommendation: ${check.recommendation}\n`)
    .join("\n");
  return `# ECS Deployment Readiness Report\n\n## Executive Summary\n\nFinal status: **${report.final_status}**\n\n## Overall Score\n\n${report.score_summary.score}%\n\n## Check Results\n\n${checkLines}\n## AI DevOps Summary\n\n${report.ai_summary}\n`;
}

export default function Report() {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchReport(reportId)
      .then(setReport)
      .catch((err) => setError(err.message));
  }, [reportId]);

  const highRisks = useMemo(
    () => report?.checks.filter((check) => check.severity === "HIGH" && check.status !== "PASS") || [],
    [report]
  );

  if (error) {
    return <div className="page"><div className="notice error">{error}</div></div>;
  }
  if (!report) {
    return <div className="page"><p className="empty-state">Loading report...</p></div>;
  }

  return (
    <div className="page">
      <header className="page-header report-header">
        <div>
          <span className="eyebrow">{report.report_id}</span>
          <h1>Readiness Report</h1>
        </div>
        <div className="button-row">
          <button onClick={() => downloadFile(`readiness-report-${report.report_id}.json`, JSON.stringify(report, null, 2), "application/json")}>
            <Download size={16} aria-hidden="true" />
            JSON
          </button>
          <button onClick={() => downloadFile(`readiness-report-${report.report_id}.md`, reportToMarkdown(report), "text/markdown")}>
            <Download size={16} aria-hidden="true" />
            Markdown
          </button>
        </div>
      </header>

      <section className="report-summary">
        <ScoreCard label="Overall score" value={`${report.score_summary.score}%`} />
        <ScoreCard label="Passed" value={report.score_summary.passed} tone="good" />
        <ScoreCard label="Warnings" value={report.score_summary.warnings} tone="warn" />
        <ScoreCard label="Failed" value={report.score_summary.failed} tone="bad" />
        <div className="status-panel">
          <span>Final status</span>
          <StatusBadge status={report.final_status} />
        </div>
      </section>

      {report.ai_summary_warning && <div className="notice warn">{report.ai_summary_warning}</div>}

      {highRisks.length > 0 && (
        <section className="panel">
          <div className="panel-header">
            <h2>High-Risk Findings</h2>
          </div>
          {highRisks.map((check) => (
            <p key={check.name} className="risk-line">{check.name}: {check.evidence}</p>
          ))}
        </section>
      )}

      <section className="checks-grid">
        {report.checks.map((check) => (
          <CheckResultCard key={check.name} check={check} />
        ))}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>AI DevOps Summary</h2>
          <span className="muted">{report.ai_summary_provider}</span>
        </div>
        <pre className="summary-block">{report.ai_summary}</pre>
      </section>
    </div>
  );
}
