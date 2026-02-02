import { Card, CardTitle } from '../components/ui'

export function DashboardPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Sensor failure prediction overview</p>
      </div>

      <Card>
        <CardTitle>Coming Soon</CardTitle>
        <p className="text-gray-600 mt-2">
          Dashboard with risk summary, recent predictions, and high-risk alerts will be implemented in Phase 4.
        </p>
      </Card>
    </div>
  )
}

export default DashboardPage
