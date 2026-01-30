# Quickstart: Moirai Sensor Failure Prediction

**Branch**: `001-moirai-sensor-prediction` | **Date**: 2026-01-30

## Prerequisites

- Python 3.11 or higher
- Railway CLI (installed and logged in)
- 2GB+ available RAM
- (Optional) CUDA-compatible GPU for faster inference

## Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd ML

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in `backend/` by pulling from Railway:

```bash
# Link to the project and pull environment variables
railway link -p "Applied-AI-Eng-Demo" -s "eaimms-staging"
railway variables > .env
```

Or create manually (get DATABASE_URL from `railway variables`):

```env
# Railway Database (get from: railway variables - DO NOT COMMIT)
DATABASE_URL=postgresql://user:password@host:port/database

# Moirai Model
MOIRAI_MODEL=Salesforce/moirai-1.0-R-base
MOIRAI_CONTEXT_LENGTH=100
MOIRAI_PREDICTION_LENGTH=24

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

Alternatively, pull from Railway:

```bash
railway link -p "Applied-AI-Eng-Demo" -s "eaimms-staging"
railway variables > .env
```

### 3. Run Database Migration

```bash
# Run migration to create moirai_predictions table
python -m migrations.run

# Or via Railway
railway run python -m migrations.run
```

### 4. Start the Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or via Railway (uses DATABASE_URL automatically)
railway run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Quick Test

### Check Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database_connected": true,
  "model_loaded": true,
  "model_version": "moirai-1.0-R-base"
}
```

### List Monitoring Points

```bash
curl http://localhost:8000/api/v1/points
```

### Get Sensor Readings

```bash
curl "http://localhost:8000/api/v1/points/{point_id}/readings"
```

### Run Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predictions/run \
  -H "Content-Type: application/json" \
  -d '{
    "point_ids": ["b35eaa48-e114-499d-a24d-3bebae6521de"]
  }'
```

### Run All Predictions

```bash
curl -X POST http://localhost:8000/api/v1/predictions/run-all
```

### View Dashboard Summary

```bash
curl http://localhost:8000/api/v1/dashboard/summary
```

### Export Predictions

```bash
# CSV export
curl "http://localhost:8000/api/v1/predictions/export?format=csv" > predictions.csv

# JSON export
curl "http://localhost:8000/api/v1/predictions/export?format=json"
```

## API Documentation

Once running, access interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deploy to Railway

### 1. Link Project

```bash
railway link -p "Applied-AI-Eng-Demo"
```

### 2. Deploy

```bash
railway up
```

### 3. Get Public URL

```bash
railway domain
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   ├── predictions.py   # Prediction endpoints
│   │   │   ├── points.py        # Monitoring points endpoints
│   │   │   ├── dashboard.py     # Dashboard summary
│   │   │   └── health.py        # Health check
│   │   └── middleware/
│   │       └── error_handler.py
│   ├── models/
│   │   ├── existing.py          # Mapped EAIMMS tables (read-only)
│   │   └── prediction.py        # MoiraiPrediction model
│   ├── services/
│   │   ├── database.py          # Railway DB connection
│   │   ├── sensor_data.py       # Fetch from EAIMMS
│   │   ├── prediction.py        # Moirai inference
│   │   └── risk_classifier.py   # Risk level logic
│   ├── schemas/
│   │   ├── request.py
│   │   └── response.py
│   └── lib/
│       ├── config.py
│       └── logging.py
├── migrations/
│   └── 001_create_moirai_predictions.sql
├── tests/
├── requirements.txt
├── Dockerfile
└── railway.toml
```

## Common Commands

```bash
# Run tests
pytest

# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type check
mypy src

# Run CLI prediction
python -m src.cli predict --point-id <uuid>

# Run all predictions via CLI
python -m src.cli predict-all
```

## Troubleshooting

### Model Loading Slow

First request may take 30-60 seconds while the Moirai model downloads (~400MB). Subsequent requests will be faster.

### Database Connection Failed

Verify Railway connection:
```bash
railway status
railway variables
```

### Insufficient Data Error

Points need at least 5 readings for prediction. Check readings count:
```bash
curl "http://localhost:8000/api/v1/points/{point_id}/readings"
```

### Out of Memory

Reduce batch size or use smaller model:
```env
MOIRAI_MODEL=Salesforce/moirai-1.0-R-small
```

## Data Flow

```
1. GET /points                    → List monitoring points from EAIMMS
2. GET /points/{id}/readings      → View time-series data
3. POST /predictions/run          → Run Moirai prediction
   └── Reads: monitoring_plans_task_results
   └── Writes: moirai_predictions
4. GET /dashboard/summary         → View risk overview
5. PATCH /predictions/{id}        → Confirm/dismiss prediction
```
