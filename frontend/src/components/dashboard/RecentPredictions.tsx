import { Link } from 'react-router-dom'
import { Card, RiskBadge, StatusBadge } from '../ui'
import type { Prediction } from '../../types/api'

interface RecentPredictionsProps {
  predictions: Prediction[]
}

export function RecentPredictions({ predictions }: RecentPredictionsProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Predictions</h3>
        <Link
          to="/predictions"
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          View all →
        </Link>
      </div>

      {predictions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No predictions yet</p>
          <p className="text-sm mt-1">Run predictions on monitoring points to see results</p>
        </div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {predictions.slice(0, 5).map((prediction) => (
            <li key={prediction.id} className="py-3">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {prediction.point_name || 'Unknown Point'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatDate(prediction.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <StatusBadge status={prediction.status} />
                  <RiskBadge level={prediction.risk_level} />
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Confidence: {prediction.confidence_score.toFixed(1)}% •
                {prediction.readings_analyzed} readings analyzed
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}

export default RecentPredictions
