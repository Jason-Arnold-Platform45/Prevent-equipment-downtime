import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { RunAllResponse } from '../types/api'

interface RunAllOptions {
  min_readings?: number
}

// Run predictions for all eligible points
export function useRunAllPredictions() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (options: RunAllOptions = {}) => {
      const params = new URLSearchParams()
      if (options.min_readings) {
        params.append('min_readings', String(options.min_readings))
      }
      const { data } = await api.post<RunAllResponse>(`/predictions/run-all?${params}`)
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

export default useRunAllPredictions
