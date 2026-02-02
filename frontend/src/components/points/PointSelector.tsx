import { useState } from 'react'
import { Button } from '../ui'
import type { Point } from '../../types/api'

interface PointSelectorProps {
  points: Point[]
  onRunPredictions: (pointIds: string[]) => void
  isLoading?: boolean
}

export function PointSelector({ points, onRunPredictions, isLoading }: PointSelectorProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Only show points with enough readings
  const eligiblePoints = points.filter((p) => p.readings_count >= 5)

  const togglePoint = (pointId: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(pointId)) {
      newSelected.delete(pointId)
    } else {
      newSelected.add(pointId)
    }
    setSelectedIds(newSelected)
  }

  const selectAll = () => {
    setSelectedIds(new Set(eligiblePoints.map((p) => p.id)))
  }

  const clearSelection = () => {
    setSelectedIds(new Set())
  }

  const handleSubmit = () => {
    onRunPredictions(Array.from(selectedIds))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {selectedIds.size} of {eligiblePoints.length} points selected
        </div>
        <div className="space-x-2">
          <button
            onClick={selectAll}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Select All
          </button>
          <button
            onClick={clearSelection}
            className="text-sm text-gray-600 hover:text-gray-800"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-md">
        {eligiblePoints.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No points with enough readings (minimum 5 required)
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {eligiblePoints.map((point) => (
              <li key={point.id}>
                <label className="flex items-center p-3 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(point.id)}
                    onChange={() => togglePoint(point.id)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div className="ml-3 flex-1">
                    <div className="text-sm font-medium text-gray-900">{point.name}</div>
                    <div className="text-xs text-gray-500">
                      {point.readings_count} readings
                    </div>
                  </div>
                </label>
              </li>
            ))}
          </ul>
        )}
      </div>

      <Button
        onClick={handleSubmit}
        disabled={selectedIds.size === 0 || isLoading}
        loading={isLoading}
        className="w-full"
      >
        Run Prediction for {selectedIds.size} Point{selectedIds.size !== 1 ? 's' : ''}
      </Button>
    </div>
  )
}

export default PointSelector
