// TypeScript types generated from OpenAPI spec
// Backend API: https://moirai-api-production.up.railway.app/api/v1

// ============================================================================
// Enums
// ============================================================================

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW'

export type PredictionStatus = 'pending' | 'confirmed' | 'dismissed'

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy'

export type ExportFormat = 'csv' | 'json'

// ============================================================================
// Core Entities
// ============================================================================

export interface Prediction {
  id: string
  point_id: string
  point_name: string | null
  equipment_id: string | null
  equipment_name: string | null
  risk_level: RiskLevel
  confidence_score: number
  predicted_failure_start: string
  predicted_failure_end: string
  context_start: string
  context_end: string
  readings_analyzed: number
  model_version: string
  status: PredictionStatus
  acknowledged_by_id: string | null
  acknowledged_at: string | null
  created_at: string
}

export interface LatestReading {
  value: number
  captured_at: string
}

export interface Point {
  id: string
  name: string
  readings_count: number
  latest_reading: LatestReading | null
  latest_prediction: Prediction | null
}

export interface Reading {
  value: number
  captured_at: string
}

// ============================================================================
// Request Types
// ============================================================================

export interface RunPredictionRequest {
  point_ids: string[]
}

export interface UpdatePredictionRequest {
  status: 'confirmed' | 'dismissed'
}

// ============================================================================
// Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PredictionListResponse extends PaginatedResponse<Prediction> {}

export interface PointListResponse extends PaginatedResponse<Point> {}

export interface RunPredictionResponse {
  predictions_created: number
  predictions: Prediction[]
  errors: Array<{
    point_id: string
    error: string
  }>
}

export interface RunAllResponse {
  eligible_points: number
  predictions_created: number
  errors_count: number
  message: string
}

export interface ReadingsResponse {
  point_id: string
  point_name: string
  readings: Reading[]
  total: number
}

export interface DashboardSummary {
  total_points: number
  points_with_predictions: number
  sensors_by_risk: {
    high: number
    medium: number
    low: number
  }
  recent_predictions: Prediction[]
  high_risk_points: Array<{
    point_id: string
    point_name: string
    confidence_score: number
    predicted_failure_start: string
  }>
}

export interface HealthResponse {
  status: HealthStatus
  database_connected: boolean
  model_loaded: boolean
  model_version: string | null
  timestamp: string
}

export interface ErrorResponse {
  error: string
  message: string
  details?: Record<string, unknown>
  timestamp: string
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface PredictionFilters {
  risk_level?: RiskLevel
  point_id?: string
  status?: PredictionStatus
  from_date?: string
  to_date?: string
  page?: number
  page_size?: number
}

export interface PointFilters {
  has_prediction?: boolean
  page?: number
  page_size?: number
}

export interface ExportFilters {
  format?: ExportFormat
  risk_level?: RiskLevel
  from_date?: string
  to_date?: string
}
