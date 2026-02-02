import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { queryKeys } from '../lib/queryClient'
import type { DashboardSummary } from '../types/api'

// Fetch dashboard summary data
export function useDashboardSummary() {
  return useQuery({
    queryKey: queryKeys.dashboard.summary,
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>('/dashboard/summary')
      return data
    },
    // Dashboard data should refresh frequently
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  })
}

export default useDashboardSummary
