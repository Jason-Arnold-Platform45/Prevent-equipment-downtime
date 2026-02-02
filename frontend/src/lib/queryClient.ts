import { QueryClient } from '@tanstack/react-query'

// Create a client with sensible defaults
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 30 seconds (data considered fresh for this duration)
      staleTime: 30 * 1000,
      // Cache time: 5 minutes (data kept in cache after becoming inactive)
      gcTime: 5 * 60 * 1000,
      // Retry failed requests up to 2 times
      retry: 2,
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus for fresh data
      refetchOnWindowFocus: true,
      // Don't refetch on mount if data is fresh
      refetchOnMount: true,
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,
    },
  },
})

// Query keys factory for consistent key management
export const queryKeys = {
  // Health
  health: ['health'] as const,

  // Points
  points: {
    all: ['points'] as const,
    list: (filters?: Record<string, unknown>) => ['points', 'list', filters] as const,
    detail: (id: string) => ['points', 'detail', id] as const,
    readings: (id: string) => ['points', 'readings', id] as const,
  },

  // Predictions
  predictions: {
    all: ['predictions'] as const,
    list: (filters?: Record<string, unknown>) => ['predictions', 'list', filters] as const,
    detail: (id: string) => ['predictions', 'detail', id] as const,
  },

  // Dashboard
  dashboard: {
    summary: ['dashboard', 'summary'] as const,
  },
} as const

export default queryClient
