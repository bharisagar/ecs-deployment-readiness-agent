export default function About() {
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">System design</span>
          <h1>Architecture</h1>
        </div>
      </header>
      <section className="architecture-grid">
        <article className="architecture-block">
          <h2>Request Flow</h2>
          <p>React submits a readiness payload to FastAPI. The backend runs local, mock, or AWS read-only checks, scores the result, writes JSON and Markdown reports, and returns the report to the UI.</p>
        </article>
        <article className="architecture-block">
          <h2>Validation Boundary</h2>
          <p>Local mode uses Docker metadata, env files, static config, and optional container probing. AWS read-only mode uses boto3 describe/get/list APIs only.</p>
        </article>
        <article className="architecture-block">
          <h2>AI Summary</h2>
          <p>Ollama runs locally through its generate API. If it is unavailable, the backend returns a deterministic rule-based DevOps summary.</p>
        </article>
        <article className="architecture-block">
          <h2>Charge Control</h2>
          <p>The backend does not create ECS services, Fargate tasks, ALBs, databases, queues, caches, or other chargeable infrastructure by default.</p>
        </article>
      </section>
      <section className="panel">
        <div className="diagram">
          <span>UI</span>
          <span>FastAPI</span>
          <span>Checks</span>
          <span>Reports</span>
          <span>Ollama</span>
          <span>AWS Read-only</span>
        </div>
      </section>
    </div>
  );
}
