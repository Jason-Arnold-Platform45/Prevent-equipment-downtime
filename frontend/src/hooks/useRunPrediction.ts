import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { RunPredictionRequest, RunPredictionResponse } from '../types/api'

// Run prediction for specific points
export function useRunPrediction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (request: RunPredictionRequest) => {
      const { data } = await api.post<RunPredictionResponse>('/predictions/run', request)
      return data
    },
    onSuccess: () => {
      // Invalidate predictions and points queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.predictions.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.points.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary })
    },
  })
}

export default useRunPrediction
