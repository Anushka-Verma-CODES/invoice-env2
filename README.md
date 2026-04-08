# Invoice & Receipt Processing Environment (OpenEnv)

OpenEnv-compliant environment for training AI agents on real-world financial workflows: field extraction, expense categorization, and anomaly detection.

## Real-World Motivation

This environment simulates the daily challenges faced by accounting teams and financial AI assistants:

- **Field Extraction**: Accurately pulling vendor names and dates from varied invoice formats
- **Expense Categorization**: Classifying expenses into Travel, Office Supplies, Utilities, or Misc
- **Anomaly Detection**: Identifying duplicate invoices and unusually high amounts that require human review

## Environment Design

### OpenEnv Specification Compliance

- `step(action) → (observation, reward, done, info)`: Process one invoice per step
- `reset() → initial observation`: Start new batch of invoices
- `state() → current state`: Environment debugging information

### Episode Structure

- **Episode**: One batch of 10 invoices (configurable)
- **Step**: Process one invoice
- **Done**: When batch is exhausted

## Observation Space

```python
Observation:
- vendor_name: str          # Invoice vendor
- invoice_date: str         # YYYY-MM-DD format
- amount: float            # Invoice total
- description: str         # Item description
- metadata: dict           # Additional context (id, raw_text, etc.)
```

## Action Space

```python
Action:
- extracted_fields: dict    # {"vendor_name": "...", "invoice_date": "..."}
- category: str            # "Travel|Office Supplies|Utilities|Misc"
- anomaly_flag: bool       # True if suspicious
```

## Reward Function

Continuous reward combining:
- **Field Extraction (40%)**: Exact match = 1.0, fuzzy >80% = partial
- **Categorization (30%)**: Correct = 1.0, close guess = 0.5
- **Anomaly Detection (30%)**: F1 score over batch

Penalties for:
- Missing required fields (-0.08 each)
- False anomaly detection (-0.12)
- Missed anomalies (-0.15)

## Tasks

### Task 1: Field Extraction (Easy)
Extract `vendor_name` and `invoice_date` from invoice text.

**Grading**: Exact match gets 1.0, fuzzy match above 0.8 gets partial credit.

### Task 2: Expense Categorization (Medium)
Classify into: Travel, Office Supplies, Utilities, Misc.

**Grading**: Correct gets 1.0, close guess gets 0.5. Supports top-2 format "A|B".

### Task 3: Anomaly Detection (Hard)
Flag duplicates and unusually high amounts (>2500).

**Grading**: Continuous F1 score using precision/recall over batch.

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone repository
git clone <repository-url>
cd invoice-env

# Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Baseline

```bash
# Heuristic baseline (no API key needed)
python scripts/run_baseline.py

# OpenAI baseline (requires API key)
export OPENAI_API_KEY="your-key-here"
export BASELINE_MODE="openai"
python scripts/run_baseline.py
```

### Run Tests

```bash
python -m pytest
```

### Docker

```bash
# Build and run
docker build -t invoice-env .
docker run invoice-env
```

## Sample Output

```
Starting baseline run (mode=heuristic)...
step=01 reward=0.700 extract=1.000 cat=1.000 anomaly=0.000
step=02 reward=0.700 extract=1.000 cat=1.000 anomaly=0.000
...
step=12 reward=0.700 extract=1.000 cat=1.000 anomaly=0.000

Episode complete
steps=12
total_score=8.400
avg_score=0.700
anomaly_counts={'tp': 0, 'fp': 0, 'fn': 4}
```

## Project Structure

```
invoice-env/
├── env/
│   ├── environment.py    # Core OpenEnv implementation
│   ├── models.py         # Pydantic schemas
│   ├── dataset.py        # Synthetic invoice generator
│   ├── tasks.py          # Task definitions & reward logic
│   └── graders.py        # Deterministic scoring functions
├── scripts/
│   └── run_baseline.py   # OpenAI + heuristic baseline
├── openenv.yaml          # Environment specification
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container for baseline execution
└── README.md            # This file
```

## Team Division

**Person 1 (Core Environment)**: `environment.py`, `models.py`, `openenv.yaml`, step/reset/state logic

**Person 2 (Data + Logic)**: `dataset.py`, `tasks.py`, `graders.py`, reward function

**Person 3 (Integration + Deployment)**: `run_baseline.py`, `Dockerfile`, `README.md`, `requirements.txt`

```bash
pip install openenv-core
```

Run checks:

```bash
openenv validate
bash validate-submission.sh <your-space-url>
```

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
    category: Optional[str] = None
    anomaly_flag: Optional[bool] = None

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
├── .env.example             # Root inference env template
├── validate-submission.sh   # Root wrapper for organizer validator script
├── Dockerfile               # Containerized baseline execution
└── requirements.txt         # Core environment dependencies
```

## Baseline Agent

Two baseline entrypoints are provided:

- `inference.py` (root): hackathon submission script (mandatory filename)
- `scripts/run_baseline.py`: developer helper script with local heuristic mode

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

## Hackathon Submission Contract

### Required Runtime Variables

Set these variables before running `inference.py`:

- `API_BASE_URL`: API endpoint for the LLM provider
- `MODEL_NAME`: model identifier for inference
- `HF_TOKEN`: API key/token used by OpenAI client
- `LOCAL_IMAGE_NAME`: local image reference if organizer uses image-backed env constructor

Reference file:

- `.env.example`

Optional reproducibility variables:

- `BATCH_SIZE` (default `24`)
- `SEED` (default `42`)

### Mandatory Inference Script

The submission inference script is:

- `inference.py` (at repository root)

It uses the OpenAI Python client for all LLM calls and reads credentials/config from the environment variables above.

### Structured Stdout Format

`inference.py` emits strict tagged logs:

- `[START]` once at run start
- `[STEP]` once per environment step
- `[END]` once at run completion

Example:

```text
[START] task=invoice-processing env=invoice-openenv model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action={"extracted_fields":{"vendor_name":"Amazon","invoice_date":"2026-01-12"},"category":"Office Supplies","anomaly_flag":false} reward=0.70 done=false error=null
[END] success=true steps=24 score=0.70 rewards=0.70,0.70,0.70
```

Required line schema (field order preserved):

- `[START] task=<task_name> env=<benchmark> model=<model_name>`
- `[STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>`
- `[END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>`

Run command:

```bash
python inference.py
```

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

Reference file:

- `backend/.env.example`

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Optional frontend environment variable:

- `VITE_API_BASE_URL` (default `http://localhost:8000/api`)

Reference file:

- `frontend/.env.example`

## API Endpoints

- `POST /api/reset`
- `POST /api/step`
- `GET /api/state`
- `POST /api/run-agent`
- `GET /api/results`

These endpoints allow both interactive stepping and full-episode automated agent runs.

## Deployment

### Docker

The root `Dockerfile` is configured for containerized API execution and HF Spaces compatibility.

```bash
docker build -t invoice-openenv .
docker run --rm -p 7860:7860 invoice-openenv
```

Health check examples after startup:

```bash
curl http://localhost:7860/
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{}'
curl -X POST http://localhost:7860/api/reset -H "Content-Type: application/json" -d '{"batch_size": 8}'
```

If you need the exact organizer command path from repo root:

```bash
bash validate-submission.sh <your-space-url>
```

### Hugging Face Spaces

For Spaces Docker deployment:

1. Use this repository as the Space source.
2. Select Docker SDK.
3. Add Space secrets for `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`.
4. Add `openenv` tag in Space metadata.
5. Verify the Space returns `200` on `/reset` (organizer validator check).

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

## Pre-Submission Checklist

- `openenv.yaml` includes metadata, task definitions, and typed schema references
- `env/models.py` defines typed Observation/Action/Reward Pydantic models
- `env/environment.py` implements `step()`, `reset()`, and `state()`
- 3 tasks implemented with deterministic graders and scores in `0.0..1.0`
- `inference.py` exists at root and uses OpenAI client + required env variables
- Structured logs include `[START]`, `[STEP]`, `[END]`
- Docker image builds and serves API container
- `/reset` responds successfully from deployed Space

## Organizer Validator Script

The repository includes organizer-compatible pre-validation helper:

- `scripts/validate-submission.sh`