# Tasks: Moirai Sensor Failure Prediction

**Input**: Design documents from `/specs/001-moirai-sensor-prediction/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Database**: Existing Railway PostgreSQL (eaimms-staging)
**Approach**: Read sensor data from existing tables, write predictions to new `moirai_predictions` table

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup ✅

**Purpose**: Project initialization and Railway database connection

- [x] T001 Create backend project structure: backend/src/{api,models,services,schemas,lib}/, backend/tests/, backend/migrations/
- [x] T002 Initialize Python project with pyproject.toml including fastapi, uvicorn, uni2ts, torch, sqlalchemy, psycopg2-binary, pydantic, gluonts, python-dotenv
- [x] T003 [P] Create requirements.txt with pinned versions
- [x] T004 [P] Create .env.example with DATABASE_URL, MOIRAI_MODEL, API_HOST, API_PORT variables
- [x] T005 [P] Create Dockerfile for Railway deployment
- [x] T006 [P] Create railway.toml with service configuration

---

## Phase 2: Foundational (Database & Core Infrastructure) ✅

**Purpose**: Connect to EAIMMS database and set up core infrastructure

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement environment config in backend/src/lib/config.py loading DATABASE_URL from Railway environment
- [x] T008 [P] Implement structured logging in backend/src/lib/logging.py
- [x] T009 Implement Railway database connection in backend/src/services/database.py with SQLAlchemy async engine
- [x] T010 Map existing EAIMMS tables (read-only) in backend/src/models/existing.py: MonitoringPoint, MonitoringTask, MonitoringTaskResult, Equipment
- [x] T011 Create MoiraiPrediction model in backend/src/models/prediction.py per data-model.md
- [x] T012 Create SQL migration in backend/migrations/001_create_moirai_predictions.sql per data-model.md
- [x] T013 Implement global error handler in backend/src/api/middleware/error_handler.py
- [x] T014 Create FastAPI app entry point in backend/src/api/main.py with CORS, error handlers, lifespan for model loading
- [x] T015 [P] Implement health check endpoint in backend/src/api/routes/health.py returning db_connected and model_loaded status
- [x] T016 [P] Create Pydantic request schemas in backend/src/schemas/request.py (RunPredictionRequest, UpdatePredictionRequest)
- [x] T017 [P] Create Pydantic response schemas in backend/src/schemas/response.py (PredictionResponse, PointResponse, DashboardSummary)

**Checkpoint**: ✅ Can connect to Railway database and run migrations

---

## Phase 3: User Story 1 - Predict Sensor Failure (Priority: P1) 🎯 MVP ✅

**Goal**: Fetch sensor data from EAIMMS, run Moirai predictions, write results back

**Independent Test**: Call POST /api/v1/predictions/run with a point_id, verify prediction is created in moirai_predictions table with risk_level and confidence_score

### Implementation

- [x] T018 [US1] Implement sensor data fetcher in backend/src/services/sensor_data.py - query monitoring_plans_task_results by point_id, return time-series DataFrame
- [x] T019 [US1] Implement Moirai model loader in backend/src/services/model_cache.py - load moirai-1.0-R-base, cache in memory on startup
- [x] T020 [US1] Implement prediction runner in backend/src/services/prediction.py - convert DataFrame to GluonTS format, run Moirai inference, return forecast
- [x] T021 [US1] Implement risk classifier in backend/src/services/risk_classifier.py - analyze forecast, determine risk_level (HIGH/MEDIUM/LOW) and confidence_score
- [x] T022 [US1] Implement prediction writer in backend/src/services/prediction.py - save MoiraiPrediction to database with all fields
- [x] T023 [US1] Implement POST /api/v1/predictions/run endpoint in backend/src/api/routes/predictions.py - accepts point_ids, orchestrates fetch→predict→save flow
- [x] T024 [US1] Implement POST /api/v1/predictions/run-all endpoint in backend/src/api/routes/predictions.py - finds all points with ≥5 readings, runs predictions
- [x] T025 [US1] Implement GET /api/v1/predictions endpoint in backend/src/api/routes/predictions.py - list with filtering by risk_level, point_id, status, date range
- [x] T026 [US1] Implement GET /api/v1/predictions/{id} endpoint in backend/src/api/routes/predictions.py
- [x] T027 [US1] Add error handling for insufficient data (<5 readings) and model failures with clear error messages
- [x] T028 [US1] Implement GET /api/v1/points endpoint in backend/src/api/routes/points.py - list monitoring points with latest prediction joined
- [x] T029 [US1] Implement GET /api/v1/points/{id}/readings endpoint in backend/src/api/routes/points.py - return time-series data for a point

**Checkpoint**: ✅ Can run predictions via API and see results in database

---

## Phase 4: User Story 2 - View Risk Dashboard (Priority: P2) ✅

**Goal**: Provide summary statistics and risk overview for EAIMMS dashboard integration

**Independent Test**: Call GET /api/v1/dashboard/summary, verify response contains sensors_by_risk counts and high_risk_points list

### Implementation

- [x] T030 [US2] Implement GET /api/v1/dashboard/summary endpoint in backend/src/api/routes/dashboard.py - return total_points, sensors_by_risk (high/medium/low counts), recent_predictions, high_risk_points
- [x] T031 [US2] Add query for points with equipment context in backend/src/services/sensor_data.py - join equipments_equipment when available
- [x] T032 [US2] Implement PATCH /api/v1/predictions/{id} endpoint in backend/src/api/routes/predictions.py - update status to confirmed/dismissed, set acknowledged_by_id

**Checkpoint**: ✅ Dashboard summary endpoint returns actionable risk data

---

## Phase 5: User Story 3 - Export Predictions (Priority: P3) ✅

**Goal**: Export prediction results for maintenance planning integration

**Independent Test**: Call GET /api/v1/predictions/export?format=csv, verify CSV file with all prediction fields

### Implementation

- [x] T033 [US3] Implement GET /api/v1/predictions/export endpoint in backend/src/api/routes/predictions.py - support format=csv|json, filtering by risk_level and date range
- [x] T034 [US3] Implement CSV streaming response for large exports in backend/src/api/routes/predictions.py

**Checkpoint**: ✅ Can export predictions in CSV/JSON format

---

## Phase 6: Polish & Deployment

**Purpose**: Production readiness and deployment to Railway

- [ ] T035 [P] Add CLI command for batch predictions in backend/src/cli.py using Typer
- [ ] T036 [P] Create sample data loader script in backend/scripts/seed_test_data.py for local testing
- [x] T037 Run migration on Railway database: railway run python -m migrations.run
- [ ] T038 Deploy to Railway: railway up
- [ ] T039 [P] Update quickstart.md with actual Railway deployment commands
- [ ] T040 Test full prediction flow on Railway deployment
- [ ] T041 [P] Add request logging middleware in backend/src/api/middleware/logging.py

---

## Bug Fixes Applied

- [x] T042 Fix sensor_data.py to join through MonitoringTask table (readings link to points via tasks, not directly)
- [x] T043 Remove references to non-existent equipment relationship on MonitoringPoint model
- [x] T044 Fix enum/string handling for risk_level and status fields (DB stores strings)
- [x] T045 Enable mock inference when Moirai model is not loaded for testing

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────┐
                                                         │
Phase 2 (Foundational) ──────────────────────────────────┤
    └── DB connection, models, migrations                │
                                                         ▼
Phase 3 (US1: Predictions) ◄─────────────────────── BLOCKS ALL
    └── Core prediction flow                             │
                                                         │
Phase 4 (US2: Dashboard) ────────────────────────────────┤
    └── Can start after Phase 2, uses US1 data           │
                                                         │
Phase 5 (US3: Export) ───────────────────────────────────┤
    └── Can start after Phase 2, uses US1 data           │
                                                         ▼
Phase 6 (Polish & Deploy) ◄────────────────────── AFTER US1+
```

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006 can all run in parallel

**Phase 2**: T008, T015, T016, T017 can run in parallel after T007, T009

**Phase 3**: T028, T029 can run in parallel with T023-T027

**Phase 4-5**: Can run in parallel after Phase 2 completes

**Phase 6**: T035, T036, T039, T041 can run in parallel

---

## Implementation Strategy

### MVP First (Phase 1-3)

1. ✅ Complete Phase 1: Setup (T001-T006)
2. ✅ Complete Phase 2: Foundational (T007-T017)
3. ✅ Complete Phase 3: User Story 1 (T018-T029)
4. ✅ **STOP and VALIDATE**: Test prediction via API call
5. Deploy to Railway with T037-T038

### Incremental Delivery

1. ✅ Setup + Foundational → Railway connection working
2. ✅ Add US1 → **MVP: Predictions running** ✓
3. ✅ Add US2 → Dashboard integration ready
4. ✅ Add US3 → Export capability
5. Polish → Production ready (in progress)

---

## Key Implementation Notes

### Database Connection

```python
# backend/src/services/database.py
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway injects this
engine = create_async_engine(DATABASE_URL)
```

### Sensor Data Query

```python
# backend/src/services/sensor_data.py
# Fixed: Must join through MonitoringTask to get readings for a point
async def get_point_readings(point_id: UUID) -> pd.DataFrame:
    query = (
        select(MonitoringTaskResult.captured_at, MonitoringTaskResult.data)
        .join(MonitoringTask, MonitoringTaskResult.task_id == MonitoringTask.id)
        .where(MonitoringTask.point_id == point_id)
        .order_by(MonitoringTaskResult.captured_at.asc())
    )
```

### Moirai Prediction

```python
# backend/src/services/model_cache.py
from uni2ts.model.moirai import MoiraiForecast, MoiraiModule

model = MoiraiForecast(
    module=MoiraiModule.from_pretrained("Salesforce/moirai-1.0-R-base"),
    prediction_length=24,
    context_length=100,
    num_samples=100
)
```

### Risk Classification

```python
# backend/src/services/risk_classifier.py
def classify_risk(forecast_mean: float, forecast_std: float, threshold: float) -> tuple[str, float]:
    confidence = min(100, max(0, (1 - forecast_std/forecast_mean) * 100))

    if forecast_mean > threshold * 1.5 and confidence >= 75:
        return "HIGH", confidence
    elif forecast_mean > threshold or confidence >= 50:
        return "MEDIUM", confidence
    return "LOW", confidence
```

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 45 |
| Phase 1 (Setup) | 6/6 ✅ |
| Phase 2 (Foundational) | 11/11 ✅ |
| Phase 3 (US1 - MVP) | 12/12 ✅ |
| Phase 4 (US2) | 3/3 ✅ |
| Phase 5 (US3) | 2/2 ✅ |
| Phase 6 (Polish) | 1/7 |
| Bug Fixes | 4/4 ✅ |

**MVP Scope**: T001-T029 (29 tasks) delivers working prediction API connected to EAIMMS database. ✅ **COMPLETE**

**Current Status**: All core functionality implemented and tested locally. Ready for Railway deployment.
