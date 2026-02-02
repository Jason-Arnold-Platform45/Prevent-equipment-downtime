import { Link } from 'react-router-dom'
import { Card, RiskBadge } from '../ui'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface HighRiskPoint {
  point_id: string
  point_name: string
  confidence_score: number
  predicted_failure_start: string
}

interface HighRiskAlertsProps {
  points: HighRiskPoint[]
}

export function HighRiskAlerts({ points }: HighRiskAlertsProps) {
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
      <div className="flex items-center gap-2 mb-4">
        <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
        <h3 className="text-lg font-semibold text-gray-900">High Risk Alerts</h3>
      </div>

      {points.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No high-risk sensors detected</p>
          <p className="text-sm mt-1">All monitored sensors are within safe parameters</p>
        </div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {points.map((point) => (
            <li key={point.point_id} className="py-3">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <Link
                    to={`/points`}
                    className="text-sm font-medium text-gray-900 hover:text-blue-600"
                  >
                    {point.point_name}
                  </Link>
                  <p className="text-xs text-gray-500 mt-1">
                    Predicted failure: {formatDate(point.predicted_failure_start)}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <span className="text-sm font-medium text-gray-700">
                    {point.confidence_score.toFixed(0)}%
                  </span>
                  <RiskBadge level="HIGH" />
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {points.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <Link
            to="/predictions?risk_level=HIGH"
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            View all high-risk predictions →
          </Link>
        </div>
      )}
    </Card>
  )
}

export default HighRiskAlerts
