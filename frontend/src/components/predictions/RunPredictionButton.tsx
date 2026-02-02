import { Button } from '../ui'
import { useRunAllPredictions } from '../../hooks'

interface RunPredictionButtonProps {
  onSuccess?: (result: { eligible_points: number; predictions_created: number }) => void
  onError?: (error: Error) => void
  minReadings?: number
}

export function RunPredictionButton({ onSuccess, onError, minReadings = 5 }: RunPredictionButtonProps) {
  const { mutate, isPending } = useRunAllPredictions()

  const handleClick = () => {
    mutate(
      { min_readings: minReadings },
      {
        onSuccess: (data) => {
          onSuccess?.({
            eligible_points: data.eligible_points,
            predictions_created: data.predictions_created,
          })
        },
        onError: (error) => {
          onError?.(error as Error)
        },
      }
    )
  }

  return (
    <Button onClick={handleClick} loading={isPending} disabled={isPending}>
      {isPending ? 'Running Predictions...' : 'Run All Predictions'}
    </Button>
  )
}

export default RunPredictionButton
