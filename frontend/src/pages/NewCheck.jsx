import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchSampleConfig, runReadinessCheck } from "../api.js";

const numberFields = new Set(["container_port", "task_cpu", "task_memory"]);
const arrayFields = new Set(["required_env_vars", "required_dependencies"]);

export default function NewCheck() {
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchSampleConfig()
      .then((sample) => setForm(sample))
      .catch((err) => setError(err.message));
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([key, value]) => {
          if (arrayFields.has(key)) {
            return [key, String(value).split(",").map((item) => item.trim()).filter(Boolean)];
          }
          if (numberFields.has(key)) {
            return [key, Number(value)];
          }
          return [key, value];
        })
      );
      const report = await runReadinessCheck(payload);
      navigate(`/reports/${report.report_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!form) {
    return <div className="page"><p className="empty-state">Loading sample config...</p></div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Readiness input</span>
          <h1>New Readiness Check</h1>
        </div>
      </header>
      {error && <div className="notice error">{error}</div>}
      <form className="form-grid" onSubmit={handleSubmit}>
        <Field label="Docker image name" value={form.image} onChange={(value) => updateField("image", value)} wide />
        <Field label="AWS region" value={form.aws_region} onChange={(value) => updateField("aws_region", value)} />
        <Field label="AWS profile" value={form.aws_profile || ""} onChange={(value) => updateField("aws_profile", value)} />
        <label>
          <span>Mode</span>
          <select value={form.mode} onChange={(event) => updateField("mode", event.target.value)}>
            <option value="mock">mock</option>
            <option value="local">local</option>
            <option value="aws-readonly">aws-readonly</option>
          </select>
        </label>
        <Field label="Container port" type="number" value={form.container_port} onChange={(value) => updateField("container_port", value)} />
        <Field label="Health check path" value={form.health_check_path} onChange={(value) => updateField("health_check_path", value)} />
        <Field label="Required env variables" value={form.required_env_vars.join(", ")} onChange={(value) => updateField("required_env_vars", value)} wide />
        <Field label="Required dependencies" value={form.required_dependencies.join(", ")} onChange={(value) => updateField("required_dependencies", value)} />
        <Field label="Task CPU" type="number" value={form.task_cpu} onChange={(value) => updateField("task_cpu", value)} />
        <Field label="Task memory" type="number" value={form.task_memory} onChange={(value) => updateField("task_memory", value)} />
        <Field label="CloudWatch log group" value={form.cloudwatch_log_group || ""} onChange={(value) => updateField("cloudwatch_log_group", value)} wide />
        <Field label="Task execution role" value={form.task_execution_role_name || ""} onChange={(value) => updateField("task_execution_role_name", value)} />
        <Field label="ALB health check path" value={form.alb_health_check_path} onChange={(value) => updateField("alb_health_check_path", value)} />
        <Field label="Local env file path" value={form.local_env_file || ""} onChange={(value) => updateField("local_env_file", value)} />
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={Boolean(form.allow_local_container_run)}
            onChange={(event) => updateField("allow_local_container_run", event.target.checked)}
          />
          <span>Allow local container run</span>
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={Boolean(form.dependency_connectivity_check)}
            onChange={(event) => updateField("dependency_connectivity_check", event.target.checked)}
          />
          <span>Dependency connectivity check</span>
        </label>
        <div className="form-actions">
          <button className="primary-action" disabled={submitting} type="submit">
            {submitting ? "Running..." : "Run Check"}
          </button>
        </div>
      </form>
    </div>
  );
}

function Field({ label, value, onChange, type = "text", wide = false }) {
  return (
    <label className={wide ? "wide" : ""}>
      <span>{label}</span>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
