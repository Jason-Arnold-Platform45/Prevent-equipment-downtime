import { Card, CardTitle } from '../components/ui'

export function PredictionsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Predictions</h1>
        <p className="text-gray-600">View and manage sensor failure predictions</p>
      </div>

      <Card>
        <CardTitle>Coming Soon</CardTitle>
        <p className="text-gray-600 mt-2">
          Predictions list with filtering and run prediction actions will be implemented in Phase 3.
        </p>
      </Card>
    </div>
  )
}

export default PredictionsPage
