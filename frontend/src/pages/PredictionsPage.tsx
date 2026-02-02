import { useState } from 'react'
import { Card, CardTitle, PageSpinner, Button } from '../components/ui'
import { PredictionsList, PredictionCard, RunPredictionButton } from '../components/predictions'
import { usePredictions } from '../hooks'
import type { Prediction, RiskLevel, PredictionStatus } from '../types/api'

export function PredictionsPage() {
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null)
  const [filters, setFilters] = useState<{
    risk_level?: RiskLevel
    status?: PredictionStatus
    page: number
  }>({ page: 1 })

  const { data, isLoading, error, refetch } = usePredictions({
    ...filters,
    page_size: 20,
  })

  const handleRunSuccess = (result: { eligible_points: number; predictions_created: number }) => {
    alert(`Created ${result.predictions_created} predictions for ${result.eligible_points} eligible points`)
    refetch()
  }

  const handleRunError = (error: Error) => {
    alert(`Error: ${error.message}`)
  }

  if (isLoading) {
    return <PageSpinner />
  }

  if (error) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600 mb-4">Error loading predictions</p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      </Card>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Predictions</h1>
          <p className="text-gray-600">View and manage sensor failure predictions</p>
        </div>
        <RunPredictionButton onSuccess={handleRunSuccess} onError={handleRunError} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card padding="none">
            {/* Filters */}
            <div className="p-4 border-b border-gray-200 flex gap-4">
              <select
                value={filters.risk_level || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    risk_level: (e.target.value as RiskLevel) || undefined,
                    page: 1,
                  })
                }
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="">All Risk Levels</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>

              <select
                value={filters.status || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    status: (e.target.value as PredictionStatus) || undefined,
                    page: 1,
                  })
                }
                className="border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </div>

            {/* Predictions List */}
            <PredictionsList
              predictions={data?.items || []}
              onSelectPrediction={setSelectedPrediction}
            />

            {/* Pagination */}
            {data && data.total_pages > 1 && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Page {data.page} of {data.total_pages} ({data.total} total)
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={data.page <= 1}
                    onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={data.page >= data.total_pages}
                    onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div>
          {selectedPrediction ? (
            <PredictionCard prediction={selectedPrediction} />
          ) : (
            <Card>
              <CardTitle>Prediction Details</CardTitle>
              <p className="text-gray-500 mt-2">
                Select a prediction from the list to view details
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default PredictionsPage
