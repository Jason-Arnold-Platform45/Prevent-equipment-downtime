import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, RiskBadge, StatusBadge } from '../ui'
import type { Prediction } from '../../types/api'

interface PredictionsListProps {
  predictions: Prediction[]
  onSelectPrediction?: (prediction: Prediction) => void
}

export function PredictionsList({ predictions, onSelectPrediction }: PredictionsListProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatShortDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  if (predictions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No predictions found</p>
        <p className="text-sm mt-1">Run predictions on monitoring points to see results here</p>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow hoverable={false}>
          <TableHead>Point</TableHead>
          <TableHead>Risk Level</TableHead>
          <TableHead>Confidence</TableHead>
          <TableHead>Predicted Failure</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {predictions.map((prediction) => (
          <TableRow
            key={prediction.id}
            onClick={() => onSelectPrediction?.(prediction)}
            className={onSelectPrediction ? 'cursor-pointer' : ''}
          >
            <TableCell className="font-medium">
              {prediction.point_name || 'Unknown Point'}
            </TableCell>
            <TableCell>
              <RiskBadge level={prediction.risk_level} />
            </TableCell>
            <TableCell>
              <span className="font-medium">{prediction.confidence_score.toFixed(1)}%</span>
            </TableCell>
            <TableCell>
              <div className="text-sm">
                <div>{formatShortDate(prediction.predicted_failure_start)}</div>
                <div className="text-gray-500 text-xs">
                  to {formatShortDate(prediction.predicted_failure_end)}
                </div>
              </div>
            </TableCell>
            <TableCell>
              <StatusBadge status={prediction.status} />
            </TableCell>
            <TableCell className="text-gray-500 text-sm">
              {formatDate(prediction.created_at)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default PredictionsList
