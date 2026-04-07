# Invoice & Receipt Processing Environment

An OpenEnv-compliant backend environment that simulates real-world invoice operations for AI agents. The agent must process a batch of invoices and solve three tasks per step:

- Easy: Field extraction (`vendor_name`, `invoice_date`)
- Medium: Expense categorization (`Travel`, `Office Supplies`, `Utilities`, `Misc`)
- Hard: Anomaly detection (`duplicate_invoice`, `unusually_high_amount`)

## Why This Matters

Finance teams process high-volume invoices with variable formatting and risk exposure. This environment models common accounting automation challenges where an agent must:

- Parse key fields reliably
- Route expenses into correct ledger buckets
- Catch suspicious entries before payment

## OpenEnv Design

The environment implements the required API:

# Invoice & Receipt Processing Platform (OpenEnv + AI Agents)

Production-ready, hackathon-grade SaaS-style platform for automated invoice intelligence.

This repository now includes:

- OpenEnv simulation and deterministic graders
- FastAPI backend with MongoDB integration
- React + Vite + Tailwind frontend dashboard
- OpenAI-driven batch agent execution with heuristic fallback mode

## Product Overview

Users can:

1. Load invoice batches from MongoDB
2. Run invoice processing step-by-step or full-batch AI agent
3. View extracted fields, category predictions, anomaly flags
4. Track per-step and final scores
5. Visualize score distributions in a dashboard chart

## Architecture Diagram (Text)

```text
[React Dashboard (Vite + Tailwind + Axios + Chart.js)]
								|
								v
[FastAPI API Layer]
	- /api/reset
	- /api/step
	- /api/state
	- /api/run-agent
	- /api/results
								|
								v
[OpenEnv Runtime]
	- observation/action/reward models
	- deterministic graders
	- weighted reward + penalties
								|
								v
[MongoDB Atlas]
	- invoices collection
	- runs collection
```

## Repository Structure

```text
root/
├── backend/
│   ├── env/
│   ├── api/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── db/
│   │   └── mongo.py
│   ├── main.py
│   ├── requirements.txt
│   └── render.yaml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InvoiceViewer.jsx
│   │   │   ├── AgentOutput.jsx
│   │   │   ├── ScoreBoard.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── services/api.js
│   │   └── App.jsx
│   ├── package.json
│   └── vercel.json
└── README.md
```

## Backend Setup (FastAPI)

1. Create and activate a Python environment.
2. Install backend dependencies.

```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
OPENAI_API_KEY=your_key_here
MONGO_URI=your_mongo_uri
MONGO_DB_NAME=invoice_platform
FRONTEND_ORIGIN=http://localhost:5173
```

4. Start backend server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend API base URL:

- `VITE_API_BASE_URL` (default: `http://localhost:8000/api`)

## API Documentation

### POST /api/reset

Starts a new episode and loads a Mongo-backed invoice batch.

Request:

```json
{
	"batch_size": 12
}
```

Response (sample):

```json
{
	"observation": {
		"vendor_name": "Amazon",
		"invoice_date": "2026-01-12",
		"amount": 118.25,
		"description": "Printer paper and pens",
		"metadata": {
			"id": "invoice-010",
			"invoice_ref": "INV-1010",
			"raw_text": "Vendor: Amazon | Date: 2026-01-12 | Amount: 118.25 | Description: Printer paper and pens",
			"line_items": [{"item": "Primary charge", "quantity": 1, "unit_price": 118.25}],
			"anomaly_type": "none"
		}
	},
	"state": {
		"pointer": 0,
		"remaining": 12,
		"total_reward": 0.0,
		"steps": 0
	}
}
```

### POST /api/step

Steps the environment using user/agent action.

Request:

```json
{
	"action": {
		"extracted_fields": {
			"vendor_name": "Amazon",
			"invoice_date": "2026-01-12"
		},
		"category": "Office Supplies",
		"anomaly_flag": false
	}
}
```

Response includes `observation`, `reward`, `done`, `info`.

### GET /api/state

Returns current environment state and last step result.

### POST /api/run-agent

Runs full-batch agent processing and stores run in MongoDB.

Request:

```json
{
	"batch_size": 12,
	"mode": "auto"
}
```

Modes:

- `auto`: OpenAI if key exists, else heuristic
- `openai`: enforce OpenAI API
- `heuristic`: offline local mode

### GET /api/results

Returns latest run and recent run history.

## MongoDB Collections

### invoices

- vendor_name
- invoice_date
- amount
- description
- category
- anomaly_flag

### runs

- run_id
- mode
- results
- final_score
- steps
- timestamp

## Demo UX Flow

1. User clicks **Reset Environment**
2. First invoice appears in Invoice Viewer
3. User clicks **Run Agent** or **Next Step**
4. UI updates with extracted fields, category, anomaly, reward
5. Final chart and run summary appear after batch completion

## Deployment

### Backend on Render

- Use `backend/render.yaml`
- Set Render env vars: `OPENAI_API_KEY`, `MONGO_URI`, `MONGO_DB_NAME`

### Frontend on Vercel

- Deploy `frontend` directory
- Set `VITE_API_BASE_URL` to deployed backend URL
- `frontend/vercel.json` handles SPA rewrites

## Team Division

### Person 1 (Backend Core)

- FastAPI APIs
- OpenEnv integration
- MongoDB connection and state orchestration

### Person 2 (AI + Data)

- dataset generation
- deterministic graders and reward logic
- OpenAI agent prompt and parsing

### Person 3 (Frontend + DevOps)

- React dashboard UI
- API integration and charting
- deployment configs (Render + Vercel)

## Screenshots (Placeholders)

- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/agent-output.png`
- `docs/screenshots/results-chart.png`

## Local Quality Checks

```bash
python -m pytest -q
python -m compileall backend
```