# Tasks: Moirai Sensor Prediction Frontend

**Input**: Design documents from `/specs/001-moirai-sensor-prediction/`
**Prerequisites**: plan.md, spec.md, contracts/openapi.yaml
**Backend API**: `https://moirai-api-production.up.railway.app` (deployed and working)

**Tech Stack**: React 18 + TypeScript + Vite + TailwindCSS + React Query
**Approach**: Build dashboard UI that consumes the existing Moirai prediction API

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup ✅

**Purpose**: Project initialization and development environment

- [x] T001 Create frontend project with Vite: `npm create vite@latest frontend -- --template react-ts`
- [x] T002 Install core dependencies: `npm install @tanstack/react-query axios react-router-dom`
- [x] T003 [P] Install UI dependencies: `npm install tailwindcss postcss autoprefixer @headlessui/react @heroicons/react`
- [x] T004 [P] Configure TailwindCSS in frontend/tailwind.config.js and frontend/postcss.config.js
- [x] T005 [P] Create .env.example with VITE_API_URL=https://moirai-api-production.up.railway.app/api/v1
- [x] T006 [P] Configure ESLint and Prettier in frontend/

---

## Phase 2: Foundational (Core Infrastructure) ✅

**Purpose**: API client, types, and shared components that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create API client with Axios in frontend/src/lib/api.ts - base URL from env, error handling
- [x] T008 [P] Generate TypeScript types from OpenAPI in frontend/src/types/api.ts (Prediction, Point, DashboardSummary, etc.)
- [x] T009 [P] Create React Query hooks setup in frontend/src/lib/queryClient.ts
- [x] T010 [P] Create shared UI components in frontend/src/components/ui/:
  - Button.tsx
  - Card.tsx
  - Badge.tsx (for risk levels: HIGH=red, MEDIUM=yellow, LOW=green)
  - Spinner.tsx
  - Table.tsx
- [x] T011 [P] Create layout components in frontend/src/components/layout/:
  - AppLayout.tsx (sidebar + main content area)
  - Header.tsx
  - Sidebar.tsx
- [x] T012 Create router setup in frontend/src/App.tsx with React Router
- [x] T013 [P] Create error boundary component in frontend/src/components/ErrorBoundary.tsx

**Checkpoint**: Can run `npm run dev` and see basic layout with navigation ✅

---

## Phase 3: User Story 1 - Run Predictions (Priority: P1) MVP ✅

**Goal**: Allow users to trigger predictions and view results for monitoring points

**Independent Test**: User can click "Run Predictions", see loading state, and view created predictions in a list

### Implementation

- [x] T014 [US1] Create usePoints hook in frontend/src/hooks/usePoints.ts - GET /points with pagination
- [x] T015 [US1] Create usePredictions hook in frontend/src/hooks/usePredictions.ts - GET /predictions with filtering
- [x] T016 [US1] Create useRunPrediction mutation in frontend/src/hooks/useRunPrediction.ts - POST /predictions/run
- [x] T017 [US1] Create useRunAllPredictions mutation in frontend/src/hooks/useRunAllPredictions.ts - POST /predictions/run-all
- [x] T018 [P] [US1] Create PointsTable component in frontend/src/components/points/PointsTable.tsx - display points with readings count
- [x] T019 [P] [US1] Create PointSelector component in frontend/src/components/points/PointSelector.tsx - multi-select for prediction
- [x] T020 [US1] Create PredictionsList component in frontend/src/components/predictions/PredictionsList.tsx - table with risk badges
- [x] T021 [US1] Create PredictionCard component in frontend/src/components/predictions/PredictionCard.tsx - detailed view
- [x] T022 [US1] Create RunPredictionButton component in frontend/src/components/predictions/RunPredictionButton.tsx - triggers POST /predictions/run-all
- [x] T023 [US1] Create PredictionsPage in frontend/src/pages/PredictionsPage.tsx - main predictions view
- [x] T024 [US1] Create PointsPage in frontend/src/pages/PointsPage.tsx - list points with "Run Prediction" action
- [x] T025 [US1] Add routes for /predictions and /points in frontend/src/App.tsx

**Checkpoint**: Can run predictions from UI and see results ✅

---

## Phase 4: User Story 2 - View Risk Dashboard (Priority: P2) ✅

**Goal**: Provide visual summary of sensor risk levels for maintenance prioritization

**Independent Test**: User can view dashboard with risk breakdown charts and high-risk sensors highlighted

### Implementation

- [x] T026 [US2] Create useDashboardSummary hook in frontend/src/hooks/useDashboardSummary.ts - GET /dashboard/summary
- [x] T027 [P] [US2] Create RiskSummaryCard component in frontend/src/components/dashboard/RiskSummaryCard.tsx - show high/medium/low counts
- [x] T028 [P] [US2] Create RiskPieChart component in frontend/src/components/dashboard/RiskPieChart.tsx - visual breakdown (use recharts or chart.js)
- [x] T029 [P] [US2] Create HighRiskAlerts component in frontend/src/components/dashboard/HighRiskAlerts.tsx - highlighted list of high-risk points
- [x] T030 [P] [US2] Create RecentPredictions component in frontend/src/components/dashboard/RecentPredictions.tsx - timeline of recent predictions
- [x] T031 [US2] Create DashboardPage in frontend/src/pages/DashboardPage.tsx - compose all dashboard components
- [x] T032 [US2] Add dashboard route as home (/) in frontend/src/App.tsx
- [x] T033 [US2] Create useUpdatePrediction mutation in frontend/src/hooks/useUpdatePrediction.ts - PATCH /predictions/{id}
- [x] T034 [US2] Add confirm/dismiss actions to PredictionCard in frontend/src/components/predictions/PredictionCard.tsx

**Checkpoint**: Dashboard shows risk overview with actionable high-risk alerts ✅

---

## Phase 5: User Story 3 - Export Predictions (Priority: P3)

**Goal**: Enable export of prediction data for maintenance planning systems

**Independent Test**: User can click Export, select format (CSV/JSON), and download file

### Implementation

- [ ] T035 [US3] Create useExportPredictions hook in frontend/src/hooks/useExportPredictions.ts - GET /predictions/export
- [ ] T036 [P] [US3] Create ExportButton component in frontend/src/components/export/ExportButton.tsx - dropdown with CSV/JSON options
- [ ] T037 [P] [US3] Create ExportFilters component in frontend/src/components/export/ExportFilters.tsx - date range and risk level filters
- [ ] T038 [US3] Add export functionality to PredictionsPage in frontend/src/pages/PredictionsPage.tsx
- [ ] T039 [US3] Implement file download utility in frontend/src/lib/download.ts - handle blob response

**Checkpoint**: Can export filtered predictions as CSV or JSON file

---

## Phase 6: Polish & Deployment

**Purpose**: Production readiness and Railway deployment

- [ ] T040 [P] Create PointDetailPage in frontend/src/pages/PointDetailPage.tsx - show readings chart with usePointReadings hook
- [ ] T041 [P] Create PredictionDetailPage in frontend/src/pages/PredictionDetailPage.tsx - full prediction details
- [ ] T042 [P] Add loading skeletons to all data-fetching components
- [ ] T043 [P] Add empty states for no data scenarios
- [ ] T044 [P] Add toast notifications for success/error feedback (use react-hot-toast)
- [ ] T045 Implement responsive design for mobile/tablet views
- [ ] T046 [P] Create frontend/Dockerfile for Railway deployment
- [ ] T047 [P] Create frontend/railway.toml with static site config
- [ ] T048 Deploy frontend to Railway: `railway up --service moirai-dashboard`
- [ ] T049 Configure CORS in backend if needed for frontend domain
- [ ] T050 Test full E2E flow on deployed frontend

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────┐
                                                         │
Phase 2 (Foundational) ──────────────────────────────────┤
    └── API client, types, shared components             │
                                                         ▼
Phase 3 (US1: Run Predictions) ◄─────────────────── BLOCKS ALL
    └── Core prediction functionality                    │
                                                         │
Phase 4 (US2: Dashboard) ────────────────────────────────┤
    └── Can start after Phase 2                          │
                                                         │
Phase 5 (US3: Export) ───────────────────────────────────┤
    └── Can start after Phase 2                          │
                                                         ▼
Phase 6 (Polish & Deploy) ◄──────────────────────── AFTER US1+
```

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006 can all run in parallel after T001, T002

**Phase 2**: T008, T009, T010, T011, T013 can run in parallel after T007

**Phase 3**: T018, T019 can run in parallel; T020, T021, T022 can run in parallel

**Phase 4**: T027, T028, T029, T030 can all run in parallel

**Phase 5**: T036, T037 can run in parallel

**Phase 6**: T040-T047 can mostly run in parallel

---

## Implementation Strategy

### MVP First (Phase 1-3)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013)
3. Complete Phase 3: User Story 1 (T014-T025)
4. **STOP and VALIDATE**: Can run predictions and see results
5. Deploy to Railway

### Incremental Delivery

1. Setup + Foundational → Development environment ready
2. Add US1 → **MVP: Can run predictions from UI**
3. Add US2 → Dashboard with risk overview
4. Add US3 → Export capability
5. Polish → Production ready

---

## API Endpoints Reference

| Endpoint | Method | Hook | Used In |
|----------|--------|------|---------|
| /health | GET | useHealth | Header status |
| /points | GET | usePoints | PointsPage |
| /points/{id}/readings | GET | usePointReadings | PointDetailPage |
| /predictions | GET | usePredictions | PredictionsPage |
| /predictions/{id} | GET | usePrediction | PredictionDetailPage |
| /predictions/{id} | PATCH | useUpdatePrediction | PredictionCard |
| /predictions/run | POST | useRunPrediction | PointSelector |
| /predictions/run-all | POST | useRunAllPredictions | RunPredictionButton |
| /predictions/export | GET | useExportPredictions | ExportButton |
| /dashboard/summary | GET | useDashboardSummary | DashboardPage |

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 50 |
| Phase 1 (Setup) | 6 |
| Phase 2 (Foundational) | 7 |
| Phase 3 (US1 - MVP) | 12 |
| Phase 4 (US2) | 9 |
| Phase 5 (US3) | 5 |
| Phase 6 (Polish) | 11 |

**MVP Scope**: T001-T025 (25 tasks) delivers working prediction UI connected to Moirai API.

**Backend API**: Already deployed at `https://moirai-api-production.up.railway.app`
