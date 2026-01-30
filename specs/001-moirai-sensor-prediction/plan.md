# Implementation Plan: Moirai Sensor Failure Prediction

**Branch**: `001-moirai-sensor-prediction` | **Date**: 2026-01-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-moirai-sensor-prediction/spec.md`

## Summary

Build a sensor failure prediction service that:
1. **Connects to existing EAIMMS database** on Railway to read sensor time-series data
2. **Runs Moirai predictions** to identify at-risk sensors
3. **Writes predictions back** to new `moirai_predictions` table
4. **Exposes API endpoints** for triggering predictions and viewing results

Primary goal: Prevent equipment downtime by catching problems early.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, uni2ts (Moirai), PyTorch, SQLAlchemy, Pydantic, GluonTS, psycopg2
**Storage**: Existing Railway PostgreSQL (EAIMMS database - eaimms-staging service)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Railway deployment
**Project Type**: Backend API service (integrates with existing EAIMMS frontend)
**Performance Goals**: 60 seconds for predictions; 85% true positive rate
**Constraints**: <60s prediction latency; 2GB+ RAM for model; CC BY-NC 4.0 license for Moirai

## Database Integration

### Railway Connection

| Property | Value |
|----------|-------|
| Project | Applied-AI-Eng-Demo |
| Service | eaimms-staging |
| Connection | Use `railway variables` to get DATABASE_URL |

### Tables Used

**Read (existing)**:
- `monitoring_plans_task_results` - Sensor time-series data
- `monitoring_plans_points` - Sensor point definitions
- `monitoring_plans_tasks` - Links points to results
- `equipments_equipment` - Equipment context

**Write (new)**:
- `moirai_predictions` - Moirai failure predictions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | ✅ PASS | Prediction logic isolated in `services/prediction.py` |
| CLI Interface | ✅ PASS | CLI command for batch predictions included |
| Test-First | ✅ PASS | Contract tests from OpenAPI spec |
| Integration Testing | ✅ PASS | E2E prediction flow tests |
| Observability | ✅ PASS | Structured logging + health endpoint |
| Simplicity | ✅ PASS | Minimal new tables; reuses existing schema |

## Project Structure

### Documentation (this feature)

```text
specs/001-moirai-sensor-prediction/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology research and decisions
├── data-model.md        # Entity definitions (existing + new tables)
├── quickstart.md        # Developer setup guide
├── contracts/
│   └── openapi.yaml     # REST API specification
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   ├── predictions.py   # Prediction endpoints
│   │   │   ├── points.py        # Monitoring points endpoints
│   │   │   └── health.py        # Health check
│   │   └── middleware/
│   │       └── error_handler.py # Global error handling
│   ├── models/
│   │   ├── __init__.py          # SQLAlchemy setup
│   │   ├── existing.py          # Mapped existing EAIMMS tables (read-only)
│   │   └── prediction.py        # MoiraiPrediction model (new table)
│   ├── services/
│   │   ├── database.py          # Railway DB connection
│   │   ├── sensor_data.py       # Fetch sensor readings
│   │   ├── prediction.py        # Moirai model integration
│   │   └── risk_classifier.py   # Risk level classification
│   ├── schemas/
│   │   ├── request.py           # Pydantic request schemas
│   │   └── response.py          # Pydantic response schemas
│   └── lib/
│       ├── config.py            # Environment configuration
│       └── logging.py           # Structured logging setup
├── tests/
│   ├── unit/
│   │   └── test_risk_classifier.py
│   ├── integration/
│   │   └── test_prediction_flow.py
│   └── conftest.py              # Test fixtures
├── migrations/
│   └── 001_create_moirai_predictions.sql
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── railway.toml
└── .env.example
```

**Structure Decision**: Backend-only service that integrates with existing EAIMMS system. No separate frontend needed - predictions will be consumed by existing EAIMMS dashboard.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/predictions/run` | Trigger prediction for specific points |
| POST | `/api/v1/predictions/run-all` | Trigger prediction for all points with sufficient data |
| GET | `/api/v1/predictions` | List predictions with filtering |
| GET | `/api/v1/predictions/{id}` | Get prediction details |
| PATCH | `/api/v1/predictions/{id}` | Update prediction status (confirm/dismiss) |
| GET | `/api/v1/points` | List monitoring points with latest prediction |
| GET | `/api/v1/points/{id}/readings` | Get time-series data for a point |
| GET | `/api/v1/dashboard/summary` | Risk summary statistics |
| GET | `/api/v1/health` | Health check |

## Complexity Tracking

> No constitution violations requiring justification.

## Phase Outputs Summary

### Phase 0: Research (Complete)
- [research.md](./research.md) - Technology decisions documented
  - Database: Existing Railway PostgreSQL
  - ML Framework: Salesforce Moirai (uni2ts)
  - Model: moirai-1.0-R-base (91M params)

### Phase 1: Design (Complete)
- [data-model.md](./data-model.md) - Uses existing tables + new `moirai_predictions`
- [contracts/openapi.yaml](./contracts/openapi.yaml) - API specification
- [quickstart.md](./quickstart.md) - Developer setup documentation

## Next Steps

Run `/speckit.tasks` to generate implementation tasks based on this plan.
