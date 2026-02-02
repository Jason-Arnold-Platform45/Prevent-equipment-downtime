import { Card, CardTitle } from '../components/ui'

export function PointsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Monitoring Points</h1>
        <p className="text-gray-600">View sensors and their latest readings</p>
      </div>

      <Card>
        <CardTitle>Coming Soon</CardTitle>
        <p className="text-gray-600 mt-2">
          Points list with readings and prediction actions will be implemented in Phase 3.
        </p>
      </Card>
    </div>
  )
}

export default PointsPage
