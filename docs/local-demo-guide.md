# Local Demo Guide

## Run Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Run Mock Check

```bash
python -m backend.app.cli check --config examples/readiness-config.yaml
```

Mock mode works without Docker, AWS, or Ollama.

## Run Local Docker Image Check

1. Build or pull an image locally.
2. Update `examples/readiness-config.yaml` with the local image name.
3. Set `mode: local`.
4. Keep `allow_local_container_run: false` for metadata-only validation.
5. Set `allow_local_container_run: true` only when you want the tool to run and probe the container locally.

## Use Ollama

```bash
ollama pull llama3.1
ollama serve
```

The backend calls `http://localhost:11434/api/generate` by default. If Ollama is not running, reports still complete with a rule-based summary.

## Generate Report

Every API or CLI run writes:

- `reports/readiness-report-<timestamp>.json`
- `reports/readiness-report-<timestamp>.md`
