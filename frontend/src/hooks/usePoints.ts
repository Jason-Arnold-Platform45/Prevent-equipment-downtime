import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { PointListResponse, PointFilters, ReadingsResponse } from '../types/api'

// Fetch points with pagination and filtering
export function usePoints(filters: PointFilters = {}) {
  return useQuery({
    queryKey: queryKeys.points.list(filters as Record<string, unknown>),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters.has_prediction !== undefined) {
        params.append('has_prediction', String(filters.has_prediction))
      }
      if (filters.page) params.append('page', String(filters.page))
      if (filters.page_size) params.append('page_size', String(filters.page_size))

      const { data } = await api.get<PointListResponse>(`/points?${params}`)
      return data
    },
  })
}

// Fetch readings for a specific point
export function usePointReadings(pointId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.points.readings(pointId),
    queryFn: async () => {
      const { data } = await api.get<ReadingsResponse>(`/points/${pointId}/readings`)
      return data
    },
    enabled: enabled && !!pointId,
  })
}

export default usePoints
