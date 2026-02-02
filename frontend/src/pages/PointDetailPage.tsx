import { useParams, Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardTitle, Button, RiskBadge, SkeletonChart, SkeletonCard, NoReadings } from '../components/ui'
import { usePointReadings, usePredictions } from '../hooks'

export function PointDetailPage() {
  const { pointId } = useParams<{ pointId: string }>()

  const { data: readingsData, isLoading: readingsLoading, error: readingsError } = usePointReadings(pointId || '')
  const { data: predictionsData, isLoading: predictionsLoading } = usePredictions({
    point_id: pointId,
    page_size: 5,
  })

  if (!pointId) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red-600">Invalid point ID</p>
          <Link to="/points" className="text-blue-600 hover:underline mt-2 inline-block">
            Back to Points
          </Link>
        </div>
      </Card>
    )
  }

  const chartData = readingsData?.readings.map((reading) => ({
    time: new Date(reading.captured_at).toLocaleString(),
    value: reading.value,
  })) || []

  return (
    <div>
      <div className="mb-6">
        <Link to="/points" className="text-sm text-blue-600 hover:underline mb-2 inline-block">
          &larr; Back to Points
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">
          {readingsData?.point_name || `Point ${pointId}`}
        </h1>
        <p className="text-gray-600">
          {readingsData ? `${readingsData.total} readings available` : 'Loading...'}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Readings Chart */}
        <div className="lg:col-span-2">
          {readingsLoading ? (
            <SkeletonChart />
          ) : readingsError ? (
            <Card>
              <div className="text-center py-8">
                <p className="text-red-600 mb-4">Error loading readings</p>
                <Button onClick={() => window.location.reload()}>Retry</Button>
              </div>
            </Card>
          ) : chartData.length === 0 ? (
            <Card>
              <NoReadings />
            </Card>
          ) : (
            <Card>
              <CardTitle>Sensor Readings</CardTitle>
              <div className="mt-4 h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="time"
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}
        </div>

        {/* Predictions Sidebar */}
        <div>
          {predictionsLoading ? (
            <SkeletonCard />
          ) : (
            <Card>
              <CardTitle>Recent Predictions</CardTitle>
              {predictionsData?.items.length === 0 ? (
                <p className="text-gray-500 mt-4 text-sm">No predictions for this point yet.</p>
              ) : (
                <div className="mt-4 space-y-3">
                  {predictionsData?.items.map((prediction) => (
                    <Link
                      key={prediction.id}
                      to={`/predictions/${prediction.id}`}
                      className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <RiskBadge level={prediction.risk_level} />
                        <span className="text-xs text-gray-500">
                          {Math.round(prediction.confidence_score * 100)}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {new Date(prediction.predicted_failure_start).toLocaleDateString()}
                      </p>
                    </Link>
                  ))}
                </div>
              )}
              <Link
                to={`/predictions?point_id=${pointId}`}
                className="block mt-4 text-sm text-blue-600 hover:underline"
              >
                View all predictions &rarr;
              </Link>
            </Card>
          )}

          {/* Point Info Card */}
          <Card className="mt-6">
            <CardTitle>Point Information</CardTitle>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Point ID</dt>
                <dd className="text-gray-900 font-mono">{pointId}</dd>
              </div>
              {readingsData && (
                <>
                  <div>
                    <dt className="text-gray-500">Name</dt>
                    <dd className="text-gray-900">{readingsData.point_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Total Readings</dt>
                    <dd className="text-gray-900">{readingsData.total.toLocaleString()}</dd>
                  </div>
                </>
              )}
            </dl>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default PointDetailPage
