import { useState } from 'react'
import toast from 'react-hot-toast'
import { Card, PageSpinner, Button, NoPoints } from '../components/ui'
import { PointsTable } from '../components/points'
import { usePoints, useRunPrediction } from '../hooks'
import type { Point } from '../types/api'

export function PointsPage() {
  const [page, setPage] = useState(1)
  const pageSize = 20

  const { data, isLoading, error, refetch } = usePoints({
    page,
    page_size: pageSize,
  })

  const runPrediction = useRunPrediction()

  const handleRunPrediction = (point: Point) => {
    runPrediction.mutate(
      { point_ids: [point.id] },
      {
        onSuccess: (result) => {
          if (result.predictions_created > 0) {
            toast.success(`Prediction created for "${point.name}"`)
          } else if (result.errors.length > 0) {
            toast.error(`Error: ${result.errors[0].error}`)
          }
          refetch()
        },
        onError: (error) => {
          toast.error(`Error: ${error.message}`)
        },
      }
    )
  }

  if (isLoading) {
    return <PageSpinner />
  }

  if (error) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600 mb-4">Error loading points</p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      </Card>
    )
  }

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Monitoring Points</h1>
          <p className="text-gray-600">View sensors and run predictions</p>
        </div>
        <div className="text-sm text-gray-500">
          {data?.total || 0} total points
        </div>
      </div>

      <Card padding="none">
        {data?.items && data.items.length > 0 ? (
          <>
            <PointsTable
              points={data.items}
              onRunPrediction={handleRunPrediction}
            />

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  Page {page} of {totalPages} ({data.total} total)
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <NoPoints />
        )}
      </Card>
    </div>
  )
}

export default PointsPage
