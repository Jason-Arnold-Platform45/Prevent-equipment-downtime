import { useState, useRef, useEffect } from 'react'
import { Button } from '../ui'
import { ArrowDownTrayIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import type { ExportFormat } from '../../types/api'

interface ExportButtonProps {
  onExport: (format: ExportFormat) => void
  isExporting?: boolean
}

export function ExportButton({ onExport, isExporting }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleExport = (format: ExportFormat) => {
    setIsOpen(false)
    onExport(format)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="secondary"
        onClick={() => setIsOpen(!isOpen)}
        disabled={isExporting}
        loading={isExporting}
      >
        <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
        Export
        <ChevronDownIcon className="h-4 w-4 ml-2" />
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
          <div className="py-1">
            <button
              onClick={() => handleExport('csv')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              Export as CSV
            </button>
            <button
              onClick={() => handleExport('json')}
              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              Export as JSON
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ExportButton
