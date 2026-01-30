# Data Model: Moirai Sensor Failure Prediction

**Branch**: `001-moirai-sensor-prediction` | **Date**: 2026-01-30

## Overview

This feature integrates with the **existing EAIMMS database** on Railway. We read sensor data from existing tables and write predictions to a new `moirai_predictions` table.

## Entity Relationship Diagram

```
┌─────────────────────────────┐
│  EXISTING EAIMMS TABLES     │
├─────────────────────────────┤
│                             │
│  monitoring_plans_points    │◄─────┐
│  (sensor definitions)       │      │
│                             │      │
│  monitoring_plans_tasks     │◄─────┤
│  (links points to results)  │      │
│                             │      │ READ
│  monitoring_plans_task_     │◄─────┤
│  results (time-series data) │      │
│                             │      │
│  equipments_equipment       │◄─────┘
│  (equipment context)        │
│                             │
└─────────────────────────────┘
              │
              │ Moirai Analysis
              ▼
┌─────────────────────────────┐
│  NEW TABLE                  │
├─────────────────────────────┤
│                             │
│  moirai_predictions         │ WRITE
│  (failure predictions)      │
│                             │
└─────────────────────────────┘
```

---

## Existing Tables (READ ONLY)

### monitoring_plans_points

Defines sensor/monitoring points in the system.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | varchar | Point name (e.g., "Pipe #3", "Dam level") |
| location | geometry | Physical location (PostGIS) |
| plan_id | uuid | FK to monitoring_plans_plans |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last update |

**Sample Data**:
- Pipe #3, Dam level, Conveyor, Office, etc.

---

### monitoring_plans_tasks

Links monitoring points to their measurement tasks.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| label | varchar | Task label |
| instructions | text | Measurement instructions |
| type | varchar | Task type |
| task_attributes | jsonb | Additional attributes |
| values | jsonb | Expected value ranges |
| point_id | uuid | FK to monitoring_plans_points |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last update |

---

### monitoring_plans_task_results

**Primary data source** - Contains time-series sensor readings.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| data | jsonb | Sensor reading: `{"value": 15}` |
| comments | text | Optional notes |
| captured_at | timestamp | When reading was taken |
| user_id | uuid | Who recorded it |
| task_id | uuid | FK to monitoring_plans_tasks |
| plan_result_id | uuid | FK to plan results |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last update |

**Sample Time-Series**:
```
[API TEST Point]
  2023-11-06: {"value": 2}
  2023-11-28: {"value": 6}
  2024-01-19: {"value": 12}
  2024-01-23: {"value": 20}
  2024-01-24: {"value": 18}
  2024-01-30: {"value": 13}
```

---

### equipments_equipment

Equipment/asset information.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | varchar | Equipment name |
| status | enum | Equipment status |
| organisation_id | uuid | FK to organisations |
| division_id | uuid | FK to divisions |
| equipment_type_id | uuid | FK to equipment_types |
| mine_id | uuid | FK to mines |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last update |

---

### ai_assessments (Reference Pattern)

Existing AI assessment storage - used as pattern for our predictions.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| external_id | varchar | External reference |
| approved | boolean | Whether approved by user |
| status | enum | awaiting_confirmation, approved, rejected |
| deterioration_mechanism_ratings | jsonb | AI output data |
| acknowledged_by_id | uuid | User who acknowledged |
| ai_assessable_type | varchar | Polymorphic type |
| ai_assessable_id | uuid | Polymorphic ID |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last update |

---

## New Table (WRITE)

### moirai_predictions

Stores Moirai model failure predictions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK | Unique identifier |
| point_id | uuid | FK → monitoring_plans_points, not null | Analyzed sensor point |
| equipment_id | uuid | FK → equipments_equipment | Associated equipment (if linked) |
| risk_level | varchar(10) | not null | HIGH, MEDIUM, LOW |
| confidence_score | decimal(5,2) | 0-100, not null | Model confidence percentage |
| predicted_failure_start | timestamp | | Earliest predicted failure |
| predicted_failure_end | timestamp | | Latest predicted failure |
| context_start | timestamp | not null | Start of analyzed time range |
| context_end | timestamp | not null | End of analyzed time range |
| readings_analyzed | integer | not null | Number of readings used |
| forecast_values | jsonb | | Raw Moirai forecast output |
| model_version | varchar(50) | not null | Moirai model version |
| status | varchar(20) | default: 'pending' | pending, confirmed, dismissed |
| acknowledged_by_id | uuid | FK → users | User who reviewed |
| acknowledged_at | timestamp | | When reviewed |
| created_at | timestamp | not null, default: now() | Prediction generation time |

**Indexes**:
- `(point_id, created_at DESC)` - Latest prediction per point
- `(risk_level, created_at DESC)` - Dashboard filtering
- `(equipment_id, risk_level)` - Equipment risk summary
- `(status, created_at DESC)` - Pending review queue

**Risk Level Classification**:
```
HIGH:   confidence_score >= 75 AND predicted failure within 7 days
MEDIUM: confidence_score >= 50 OR predicted failure within 30 days
LOW:    All other cases
```

---

## Migration SQL

```sql
-- Create moirai_predictions table
CREATE TABLE moirai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    point_id UUID NOT NULL REFERENCES monitoring_plans_points(id),
    equipment_id UUID REFERENCES equipments_equipment(id),
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    predicted_failure_start TIMESTAMP,
    predicted_failure_end TIMESTAMP,
    context_start TIMESTAMP NOT NULL,
    context_end TIMESTAMP NOT NULL,
    readings_analyzed INTEGER NOT NULL,
    forecast_values JSONB,
    model_version VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'dismissed')),
    acknowledged_by_id UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_failure_range CHECK (
        predicted_failure_start IS NULL OR
        predicted_failure_end IS NULL OR
        predicted_failure_start <= predicted_failure_end
    ),
    CONSTRAINT valid_context_range CHECK (context_end > context_start)
);

-- Indexes for performance
CREATE INDEX idx_moirai_predictions_point_created
    ON moirai_predictions(point_id, created_at DESC);

CREATE INDEX idx_moirai_predictions_risk_created
    ON moirai_predictions(risk_level, created_at DESC);

CREATE INDEX idx_moirai_predictions_equipment_risk
    ON moirai_predictions(equipment_id, risk_level);

CREATE INDEX idx_moirai_predictions_status_created
    ON moirai_predictions(status, created_at DESC);
```

---

## Data Flow

### 1. Read Sensor Data

```sql
SELECT
    p.id as point_id,
    p.name as point_name,
    tr.data->>'value' as value,
    tr.captured_at
FROM monitoring_plans_task_results tr
JOIN monitoring_plans_tasks t ON tr.task_id = t.id
JOIN monitoring_plans_points p ON t.point_id = p.id
WHERE p.id = :point_id
ORDER BY tr.captured_at ASC
```

### 2. Transform to Moirai Format

```python
# Convert to pandas DataFrame with datetime index
df = pd.DataFrame({
    'value': [r['value'] for r in readings]
}, index=pd.DatetimeIndex([r['captured_at'] for r in readings]))

# Convert to GluonTS format
dataset = PandasDataset({'target': df['value']})
```

### 3. Write Predictions

```sql
INSERT INTO moirai_predictions (
    point_id, risk_level, confidence_score,
    predicted_failure_start, predicted_failure_end,
    context_start, context_end, readings_analyzed,
    forecast_values, model_version
) VALUES (
    :point_id, :risk_level, :confidence_score,
    :failure_start, :failure_end,
    :context_start, :context_end, :readings_count,
    :forecast_json, 'moirai-1.0-R-base'
)
```

---

## Query Patterns

### Get Latest Prediction per Point

```sql
SELECT DISTINCT ON (point_id)
    mp.*, p.name as point_name
FROM moirai_predictions mp
JOIN monitoring_plans_points p ON mp.point_id = p.id
ORDER BY point_id, created_at DESC
```

### Dashboard Summary

```sql
SELECT
    risk_level,
    COUNT(*) as count
FROM moirai_predictions
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY risk_level
```

### High Risk Points

```sql
SELECT
    p.name as point_name,
    mp.confidence_score,
    mp.predicted_failure_start,
    mp.created_at
FROM moirai_predictions mp
JOIN monitoring_plans_points p ON mp.point_id = p.id
WHERE mp.risk_level = 'HIGH'
  AND mp.status = 'pending'
ORDER BY mp.confidence_score DESC
```
