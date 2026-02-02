import { useMutation } from '@tanstack/react-query'
import api from '../lib/api'
import { downloadBlob, generateFilename } from '../lib/download'
import type { ExportFilters, ExportFormat } from '../types/api'

interface ExportParams extends ExportFilters {
  format: ExportFormat
}

// Export predictions as CSV or JSON
export function useExportPredictions() {
  return useMutation({
    mutationFn: async (params: ExportParams) => {
      const queryParams = new URLSearchParams()
      queryParams.append('format', params.format)
      if (params.risk_level) queryParams.append('risk_level', params.risk_level)
      if (params.from_date) queryParams.append('from_date', params.from_date)
      if (params.to_date) queryParams.append('to_date', params.to_date)

      const response = await api.get(`/predictions/export?${queryParams}`, {
        responseType: 'blob',
      })

      // Determine filename based on format
      const extension = params.format === 'csv' ? 'csv' : 'json'
      const filename = generateFilename('predictions-export', extension)

      // Download the file
      downloadBlob(response.data, filename)

      return { filename, format: params.format }
    },
  })
}

export default useExportPredictions
