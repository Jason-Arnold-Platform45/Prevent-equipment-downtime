import { useParams, Link } from 'react-router-dom'
import { Card, CardTitle, Button, RiskBadge, StatusBadge, SkeletonCard } from '../components/ui'
import { usePrediction, useUpdatePrediction } from '../hooks'

export function PredictionDetailPage() {
  const { predictionId } = useParams<{ predictionId: string }>()

  const { data: prediction, isLoading, error, refetch } = usePrediction(predictionId || '')
  const updatePrediction = useUpdatePrediction()

  if (!predictionId) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600">Invalid prediction ID</p>
          <Link to="/predictions" className="text-blue-600 hover:underline mt-2 inline-block">
            Back to Predictions
          </Link>
        </div>
      </Card>
    )
  }

  const handleConfirm = () => {
    updatePrediction.mutate(
      { predictionId, request: { status: 'confirmed' } },
      { onSuccess: () => refetch() }
    )
  }

  const handleDismiss = () => {
    updatePrediction.mutate(
      { predictionId, request: { status: 'dismissed' } },
      { onSuccess: () => refetch() }
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    )
  }

  if (error || !prediction) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600 mb-4">Error loading prediction</p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      </Card>
    )
  }

  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString()

  return (
    <div>
      <div className="mb-6">
        <Link to="/predictions" className="text-sm text-blue-600 hover:underline mb-2 inline-block">
          &larr; Back to Predictions
        </Link>
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">Prediction Details</h1>
          <RiskBadge level={prediction.risk_level} />
          <StatusBadge status={prediction.status} />
        </div>
        <p className="text-gray-600">{prediction.point_name || prediction.point_id}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Risk Assessment */}
          <Card>
            <CardTitle>Risk Assessment</CardTitle>
            <div className="mt-4 grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-500">Risk Level</p>
                <p className="text-lg font-semibold mt-1">
                  <RiskBadge level={prediction.risk_level} />
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Confidence Score</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {Math.round(prediction.confidence_score * 100)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Predicted Failure Window</p>
                <p className="text-gray-900 mt-1">
                  {formatDate(prediction.predicted_failure_start)}
                </p>
                <p className="text-gray-600 text-sm">
                  to {formatDate(prediction.predicted_failure_end)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Readings Analyzed</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {prediction.readings_analyzed.toLocaleString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Analysis Context */}
          <Card>
            <CardTitle>Analysis Context</CardTitle>
            <div className="mt-4 grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-500">Context Start</p>
                <p className="text-gray-900 mt-1">{formatDate(prediction.context_start)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Context End</p>
                <p className="text-gray-900 mt-1">{formatDate(prediction.context_end)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Model Version</p>
                <p className="text-gray-900 font-mono text-sm mt-1">{prediction.model_version}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created At</p>
                <p className="text-gray-900 mt-1">{formatDate(prediction.created_at)}</p>
              </div>
            </div>
          </Card>

          {/* Equipment Info */}
          {prediction.equipment_name && (
            <Card>
              <CardTitle>Equipment Information</CardTitle>
              <div className="mt-4">
                <p className="text-sm text-gray-500">Equipment</p>
                <p className="text-gray-900 mt-1">{prediction.equipment_name}</p>
                <p className="text-xs text-gray-500 font-mono mt-1">{prediction.equipment_id}</p>
              </div>
            </Card>
          )}
        </div>

        {/* Actions Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardTitle>Status</CardTitle>
            <div className="mt-4">
              <StatusBadge status={prediction.status} />
              {prediction.acknowledged_at && (
                <p className="text-sm text-gray-500 mt-3">
                  Updated: {formatDate(prediction.acknowledged_at)}
                </p>
              )}
            </div>

            {prediction.status === 'pending' && (
              <div className="mt-6 space-y-3">
                <Button
                  onClick={handleConfirm}
                  loading={updatePrediction.isPending}
                  className="w-full"
                >
                  Confirm Prediction
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleDismiss}
                  loading={updatePrediction.isPending}
                  className="w-full"
                >
                  Dismiss Prediction
                </Button>
              </div>
            )}
          </Card>

          {/* Quick Links */}
          <Card>
            <CardTitle>Quick Links</CardTitle>
            <div className="mt-4 space-y-2">
              <Link
                to={`/points/${prediction.point_id}`}
                className="block text-sm text-blue-600 hover:underline"
              >
                View Point Details &rarr;
              </Link>
              <Link
                to={`/predictions?point_id=${prediction.point_id}`}
                className="block text-sm text-blue-600 hover:underline"
              >
                All Predictions for this Point &rarr;
              </Link>
            </div>
          </Card>

          {/* Metadata */}
          <Card>
            <CardTitle>Metadata</CardTitle>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Prediction ID</dt>
                <dd className="text-gray-900 font-mono text-xs break-all">{prediction.id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Point ID</dt>
                <dd className="text-gray-900 font-mono text-xs break-all">{prediction.point_id}</dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default PredictionDetailPage
