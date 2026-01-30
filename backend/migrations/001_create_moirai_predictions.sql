-- Migration: Create moirai_predictions table
-- Date: 2026-01-30
-- Description: Table for storing Moirai model failure predictions

-- Create the table
CREATE TABLE IF NOT EXISTS moirai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- References to existing tables
    point_id UUID NOT NULL REFERENCES monitoring_plans_points(id),
    equipment_id UUID REFERENCES equipments_equipment(id),

    -- Prediction results
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    predicted_failure_start TIMESTAMP,
    predicted_failure_end TIMESTAMP,

    -- Analysis context
    context_start TIMESTAMP NOT NULL,
    context_end TIMESTAMP NOT NULL,
    readings_analyzed INTEGER NOT NULL,

    -- Model output
    forecast_values JSONB,
    model_version VARCHAR(50) NOT NULL,

    -- Review status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'dismissed')),
    acknowledged_by_id UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_failure_range CHECK (
        predicted_failure_start IS NULL OR
        predicted_failure_end IS NULL OR
        predicted_failure_start <= predicted_failure_end
    ),
    CONSTRAINT valid_context_range CHECK (context_end > context_start)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_moirai_predictions_point_created
    ON moirai_predictions(point_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_moirai_predictions_risk_created
    ON moirai_predictions(risk_level, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_moirai_predictions_equipment_risk
    ON moirai_predictions(equipment_id, risk_level);

CREATE INDEX IF NOT EXISTS idx_moirai_predictions_status_created
    ON moirai_predictions(status, created_at DESC);

-- Add comment for documentation
COMMENT ON TABLE moirai_predictions IS 'Moirai model sensor failure predictions';
COMMENT ON COLUMN moirai_predictions.risk_level IS 'HIGH: immediate attention, MEDIUM: monitor closely, LOW: normal operation';
COMMENT ON COLUMN moirai_predictions.confidence_score IS 'Model confidence percentage (0-100)';
COMMENT ON COLUMN moirai_predictions.forecast_values IS 'Raw Moirai model output for debugging';
