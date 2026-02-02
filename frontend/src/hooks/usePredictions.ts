import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { PredictionListResponse, PredictionFilters, Prediction } from '../types/api'

// Fetch predictions with pagination and filtering
export function usePredictions(filters: PredictionFilters = {}) {
  return useQuery({
    queryKey: queryKeys.predictions.list(filters as Record<string, unknown>),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters.risk_level) params.append('risk_level', filters.risk_level)
      if (filters.point_id) params.append('point_id', filters.point_id)
      if (filters.status) params.append('status', filters.status)
      if (filters.from_date) params.append('from_date', filters.from_date)
      if (filters.to_date) params.append('to_date', filters.to_date)
      if (filters.page) params.append('page', String(filters.page))
      if (filters.page_size) params.append('page_size', String(filters.page_size))

      const { data } = await api.get<PredictionListResponse>(`/predictions?${params}`)
      return data
    },
  })
}

// Fetch a single prediction by ID
export function usePrediction(predictionId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.predictions.detail(predictionId),
    queryFn: async () => {
      const { data } = await api.get<Prediction>(`/predictions/${predictionId}`)
      return data
    },
    enabled: enabled && !!predictionId,
  })
}

export default usePredictions
