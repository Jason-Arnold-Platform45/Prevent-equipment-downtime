import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Card } from '../ui'

interface RiskPieChartProps {
  sensorsByRisk: {
    high: number
    medium: number
    low: number
  }
}

const COLORS = {
  high: '#ef4444',   // red-500
  medium: '#f59e0b', // amber-500
  low: '#22c55e',    // green-500
}

export function RiskPieChart({ sensorsByRisk }: RiskPieChartProps) {
  const data = [
    { name: 'High Risk', value: sensorsByRisk.high, color: COLORS.high },
    { name: 'Medium Risk', value: sensorsByRisk.medium, color: COLORS.medium },
    { name: 'Low Risk', value: sensorsByRisk.low, color: COLORS.low },
  ].filter((item) => item.value > 0)

  const total = sensorsByRisk.high + sensorsByRisk.medium + sensorsByRisk.low

  if (total === 0) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No predictions available
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
              labelLine={false}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => [`${value} predictions`, 'Count']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}

export default RiskPieChart
