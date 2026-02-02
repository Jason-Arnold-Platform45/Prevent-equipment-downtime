import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, RiskBadge } from '../ui'
import type { Point } from '../../types/api'

interface PointsTableProps {
  points: Point[]
  onSelectPoint?: (point: Point) => void
  onRunPrediction?: (point: Point) => void
}

export function PointsTable({ points, onSelectPoint, onRunPrediction }: PointsTableProps) {
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Table>
      <TableHeader>
        <TableRow hoverable={false}>
          <TableHead>Name</TableHead>
          <TableHead>Readings</TableHead>
          <TableHead>Latest Reading</TableHead>
          <TableHead>Latest Prediction</TableHead>
          <TableHead>Risk Level</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {points.map((point) => (
          <TableRow
            key={point.id}
            onClick={() => onSelectPoint?.(point)}
            className={onSelectPoint ? 'cursor-pointer' : ''}
          >
            <TableCell className="font-medium">{point.name}</TableCell>
            <TableCell>{point.readings_count}</TableCell>
            <TableCell>
              {point.latest_reading ? (
                <div>
                  <span className="font-medium">{point.latest_reading.value.toFixed(2)}</span>
                  <span className="text-gray-500 text-xs ml-2">
                    {formatDate(point.latest_reading.captured_at)}
                  </span>
                </div>
              ) : (
                <span className="text-gray-400">No readings</span>
              )}
            </TableCell>
            <TableCell>
              {point.latest_prediction ? (
                <span className="text-xs text-gray-500">
                  {formatDate(point.latest_prediction.created_at)}
                </span>
              ) : (
                <span className="text-gray-400">-</span>
              )}
            </TableCell>
            <TableCell>
              {point.latest_prediction ? (
                <RiskBadge level={point.latest_prediction.risk_level} />
              ) : (
                <span className="text-gray-400">-</span>
              )}
            </TableCell>
            <TableCell className="text-right">
              {point.readings_count >= 5 ? (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onRunPrediction?.(point)
                  }}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Run Prediction
                </button>
              ) : (
                <span className="text-gray-400 text-sm">Need 5+ readings</span>
              )}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default PointsTable
