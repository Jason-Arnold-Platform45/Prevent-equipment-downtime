import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from 'axios'

// API base URL from environment
const API_URL = import.meta.env.VITE_API_URL || 'https://moirai-api-production.up.railway.app/api/v1'

// Create axios instance with default config
export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const data = error.response.data as { message?: string; error?: string }

      if (status === 404) {
        console.error('Resource not found:', error.config?.url)
      } else if (status === 500) {
        console.error('Server error:', data?.message || 'Internal server error')
      }

      // Enhance error with server message if available
      if (data?.message) {
        error.message = data.message
      } else if (data?.error) {
        error.message = data.error
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error - no response received')
      error.message = 'Network error. Please check your connection.'
    }

    return Promise.reject(error)
  }
)

// API error type
export interface ApiError {
  error: string
  message: string
  details?: Record<string, unknown>
  timestamp: string
}

// Helper to check if error is an API error
export function isApiError(error: unknown): error is AxiosError<ApiError> {
  return axios.isAxiosError(error)
}

// Helper to get error message
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.response?.data?.message || error.message || 'An error occurred'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unexpected error occurred'
}

export default api
