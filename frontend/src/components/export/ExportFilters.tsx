import { useState } from 'react'
import { Button } from '../ui'
import type { RiskLevel, ExportFormat } from '../../types/api'

interface ExportFiltersProps {
  onExport: (filters: {
    format: ExportFormat
    risk_level?: RiskLevel
    from_date?: string
    to_date?: string
  }) => void
  isExporting?: boolean
}

export function ExportFilters({ onExport, isExporting }: ExportFiltersProps) {
  const [riskLevel, setRiskLevel] = useState<RiskLevel | ''>('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [format, setFormat] = useState<ExportFormat>('csv')

  const handleExport = () => {
    onExport({
      format,
      risk_level: riskLevel || undefined,
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
    })
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Risk Level
          </label>
          <select
            value={riskLevel}
            onChange={(e) => setRiskLevel(e.target.value as RiskLevel | '')}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="">All Risk Levels</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Format
          </label>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value as ExportFormat)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            From Date
          </label>
          <input
            type="date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            To Date
          </label>
          <input
            type="date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>
      </div>

      <Button onClick={handleExport} disabled={isExporting} loading={isExporting} className="w-full">
        {isExporting ? 'Exporting...' : 'Export Predictions'}
      </Button>
    </div>
  )
}

export default ExportFilters
