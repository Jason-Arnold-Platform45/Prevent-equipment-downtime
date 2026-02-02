import { Card, RiskBadge, StatusBadge, Button } from '../ui'
import type { Prediction } from '../../types/api'

interface PredictionCardProps {
  prediction: Prediction
  onConfirm?: () => void
  onDismiss?: () => void
  isUpdating?: boolean
}

export function PredictionCard({ prediction, onConfirm, onDismiss, isUpdating }: PredictionCardProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Card>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {prediction.point_name || 'Unknown Point'}
          </h3>
          {prediction.equipment_name && (
            <p className="text-sm text-gray-500">{prediction.equipment_name}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <RiskBadge level={prediction.risk_level} />
          <StatusBadge status={prediction.status} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <dt className="text-sm font-medium text-gray-500">Confidence Score</dt>
          <dd className="mt-1 text-2xl font-bold text-gray-900">
            {prediction.confidence_score.toFixed(1)}%
          </dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">Readings Analyzed</dt>
          <dd className="mt-1 text-2xl font-bold text-gray-900">
            {prediction.readings_analyzed}
          </dd>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div>
          <dt className="text-sm font-medium text-gray-500">Predicted Failure Window</dt>
          <dd className="mt-1 text-sm text-gray-900">
            {formatDate(prediction.predicted_failure_start)} — {formatDate(prediction.predicted_failure_end)}
          </dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">Analysis Period</dt>
          <dd className="mt-1 text-sm text-gray-900">
            {formatDate(prediction.context_start)} — {formatDate(prediction.context_end)}
          </dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">Model Version</dt>
          <dd className="mt-1 text-sm text-gray-900">{prediction.model_version}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">Created</dt>
          <dd className="mt-1 text-sm text-gray-900">{formatDate(prediction.created_at)}</dd>
        </div>
      </div>

      {prediction.status === 'pending' && (onConfirm || onDismiss) && (
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          {onConfirm && (
            <Button
              variant="danger"
              onClick={onConfirm}
              disabled={isUpdating}
              loading={isUpdating}
              className="flex-1"
            >
              Confirm Issue
            </Button>
          )}
          {onDismiss && (
            <Button
              variant="secondary"
              onClick={onDismiss}
              disabled={isUpdating}
              className="flex-1"
            >
              Dismiss
            </Button>
          )}
        </div>
      )}

      {prediction.acknowledged_at && (
        <div className="pt-4 border-t border-gray-200 text-sm text-gray-500">
          Acknowledged on {formatDate(prediction.acknowledged_at)}
        </div>
      )}
    </Card>
  )
}

export default PredictionCard
