import { Card } from '../ui'

interface RiskSummaryCardProps {
  totalPoints: number
  pointsWithPredictions: number
  sensorsByRisk: {
    high: number
    medium: number
    low: number
  }
}

export function RiskSummaryCard({ totalPoints, pointsWithPredictions, sensorsByRisk }: RiskSummaryCardProps) {
  const stats = [
    { label: 'Total Points', value: totalPoints, color: 'text-gray-900' },
    { label: 'With Predictions', value: pointsWithPredictions, color: 'text-blue-600' },
    { label: 'High Risk', value: sensorsByRisk.high, color: 'text-red-600' },
    { label: 'Medium Risk', value: sensorsByRisk.medium, color: 'text-amber-600' },
    { label: 'Low Risk', value: sensorsByRisk.low, color: 'text-green-600' },
  ]

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Summary</h3>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="text-center">
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
          </div>
        ))}
      </div>
    </Card>
  )
}

export default RiskSummaryCard
