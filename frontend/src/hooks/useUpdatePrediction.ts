import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { Prediction, UpdatePredictionRequest } from '../types/api'

interface UpdatePredictionParams {
  predictionId: string
  request: UpdatePredictionRequest
}

// Update prediction status (confirm or dismiss)
export function useUpdatePrediction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ predictionId, request }: UpdatePredictionParams) => {
      const { data } = await api.patch<Prediction>(`/predictions/${predictionId}`, request)
      return data
    },
    onSuccess: (data) => {
      // Update the specific prediction in cache
      queryClient.setQueryData(queryKeys.predictions.detail(data.id), data)
      // Invalidate predictions list and dashboard to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.predictions.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary })
    },
  })
}

export default useUpdatePrediction
