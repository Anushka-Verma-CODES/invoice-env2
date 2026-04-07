# Invoice & Receipt Processing Platform (OpenEnv + AI Agents)

OpenEnv-compliant environment and full-stack app for invoice automation.

Core goal: train/evaluate agents to process invoices and receipts by solving three tasks in sequence:

1. Field extraction (easy)
2. Expense categorization (medium)
3. Anomaly detection (hard)

## Problem Coverage

### Task 1: Field Extraction (Easy)

- Observation: raw invoice fields and text context
- Action: extract `vendor_name`, `invoice_date`
- Reward: `+1` exact match; partial credit for fuzzy similarity `>= 0.8`
- Grader: deterministic comparison against ground truth

### Task 2: Expense Categorization (Medium)

- Observation: vendor, description, line-item metadata
- Action: assign category from `Travel`, `Office Supplies`, `Utilities`, `Misc`
- Reward: `+1` exact match; `+0.5` if correct label appears in top-2 prediction
- Grader: deterministic category check against labeled data

### Task 3: Anomaly Detection (Hard)

- Observation: invoice batch context (amount patterns, references, vendor/date behavior)
- Action: set anomaly flag for duplicate/high-risk invoices
- Reward: continuous score from precision/recall F1 behavior
- Grader: deterministic scoring function derived from confusion counts

## OpenEnv Models

Implemented with Pydantic typed models:

```python
class InvoiceObservation(BaseModel):
    vendor_name: str
    invoice_date: str
    amount: float
    description: str
    metadata: Dict[str, Any]

class InvoiceAction(BaseModel):
    extracted_fields: Dict[str, str]
    category: Optional[str]
    anomaly_flag: Optional[bool]

class InvoiceReward(BaseModel):
    score: float
    details: Dict[str, Any]
```

## Episode Definition

One episode equals processing one invoice batch. Default behavior uses deterministic synthetic invoices with anomalies included.

## Environment API

The environment follows OpenEnv-style methods:

- `reset()`
- `step(action)`
- `state()`

Implementation entrypoint and schema wiring are defined in `openenv.yaml`.

## Repository Structure

```text
.
├── env/                     # Core OpenEnv runtime (models, graders, tasks, dataset)
├── scripts/                 # Baseline agent runner (OpenAI + heuristic fallback)
├── tests/                   # Model, grader, and environment tests
├── backend/                 # FastAPI service + Mongo integration
├── frontend/                # React/Vite/Tailwind dashboard
├── openenv.yaml             # OpenEnv metadata and schema mapping
├── Dockerfile               # Containerized baseline execution
└── requirements.txt         # Core environment dependencies
```

## Baseline Agent

`scripts/run_baseline.py` supports:

- `BASELINE_MODE=auto` (default): OpenAI if API key is present, otherwise heuristic
- `BASELINE_MODE=openai`: strict OpenAI mode
- `BASELINE_MODE=heuristic`: fully offline deterministic mode

### Example

```bash
python scripts/run_baseline.py
```

Recent heuristic run output:

- Steps: 12
- Total score: 8.400
- Average score: 0.700

## Local Setup

### Core Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
python scripts/run_baseline.py
```

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Optional backend environment variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default `gpt-4o-mini`)
- `MONGO_URI`
- `MONGO_DB_NAME`
- `FRONTEND_ORIGIN`

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Optional frontend environment variable:

- `VITE_API_BASE_URL` (default `http://localhost:8000/api`)

## API Endpoints

- `POST /api/reset`
- `POST /api/step`
- `GET /api/state`
- `POST /api/run-agent`
- `GET /api/results`

These endpoints allow both interactive stepping and full-episode automated agent runs.

## Deployment

### Docker

The repository includes a root `Dockerfile` that installs core dependencies and runs the baseline script.

```bash
docker build -t invoice-openenv .
docker run --rm invoice-openenv
```

### Hugging Face Spaces

For Spaces Docker deployment:

1. Use this repository as the Space source.
2. Select Docker SDK.
3. Set secrets (`OPENAI_API_KEY`) if using OpenAI mode.
4. Optionally set `BASELINE_MODE=heuristic` for offline demo behavior.

### Full-Stack Hosting

- Backend: `backend/render.yaml` (Render)
- Frontend: `frontend/vercel.json` (Vercel)

## Validation Status

- Deterministic synthetic dataset with duplicates and high-amount anomalies
- Deterministic graders for all three tasks
- Typed observation/action/reward models
- OpenEnv metadata in `openenv.yaml`
- Baseline script with OpenAI + offline fallback
- Docker support included
- Test suite passing (`14 passed`)