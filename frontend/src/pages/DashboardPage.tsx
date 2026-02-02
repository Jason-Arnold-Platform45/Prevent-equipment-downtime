import { PageSpinner, Button, Card } from '../components/ui'
import {
  RiskSummaryCard,
  RiskPieChart,
  HighRiskAlerts,
  RecentPredictions,
} from '../components/dashboard'
import { RunPredictionButton } from '../components/predictions'
import { useDashboardSummary } from '../hooks/useDashboardSummary'

export function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboardSummary()

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
          <p className="text-red-600 mb-4">Error loading dashboard</p>
          <Button onClick={() => refetch()}>Retry</Button>
        </div>
      </Card>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Sensor failure prediction overview</p>
        </div>
        <RunPredictionButton onSuccess={handleRunSuccess} onError={handleRunError} />
      </div>

      {/* Risk Summary */}
      <div className="mb-6">
        <RiskSummaryCard
          totalPoints={data.total_points}
          pointsWithPredictions={data.points_with_predictions}
          sensorsByRisk={data.sensors_by_risk}
        />
      </div>

      {/* Charts and Alerts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <RiskPieChart sensorsByRisk={data.sensors_by_risk} />
        <HighRiskAlerts points={data.high_risk_points} />
      </div>

      {/* Recent Predictions */}
      <RecentPredictions predictions={data.recent_predictions} />
    </div>
  )
}

export default DashboardPage
