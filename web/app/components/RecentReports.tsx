'use client'

import { useState, useEffect } from 'react'
import { FileText, Calendar, AlertTriangle, CheckCircle, Info } from 'lucide-react'
import { AnalysisResult } from '../utils/export'

interface Report {
  id: number
  doc_name: string
  summary: string
  overall_risk: number
  flags: Array<{
    title: string
    severity: number
    why_it_matters: string
    recommendation: string
    evidence: Array<{
      page: number
      quote: string
    }>
  }>
  ts: number
}

interface RecentReportsProps {
  onReportSelect: (result: AnalysisResult, docName: string) => void
}

export function RecentReports({ onReportSelect }: RecentReportsProps) {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const response = await fetch('http://localhost:8000/reports?user_id=demo_user')
      if (!response.ok) {
        throw new Error('Failed to fetch reports')
      }
      const data = await response.json()
      setReports(data.reports || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reports')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk >= 80) return 'text-red-600 dark:text-red-400'
    if (risk >= 60) return 'text-orange-600 dark:text-orange-400'
    if (risk >= 40) return 'text-yellow-600 dark:text-yellow-400'
    if (risk >= 20) return 'text-green-600 dark:text-green-400'
    return 'text-green-600 dark:text-green-400'
  }

  const getSeverityIcon = (maxSeverity: number) => {
    if (maxSeverity >= 4) return <AlertTriangle className="h-4 w-4 text-red-500" />
    if (maxSeverity >= 3) return <Info className="h-4 w-4 text-yellow-500" />
    return <CheckCircle className="h-4 w-4 text-green-500" />
  }

  const handleReportClick = (report: Report) => {
    const result: AnalysisResult = {
      summary: report.summary,
      overall_risk: report.overall_risk,
      flags: report.flags
    }
    onReportSelect(result, report.doc_name)
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Reports</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Reports</h3>
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (reports.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Reports</h3>
        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No reports yet. Upload a document to get started!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Reports</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {reports.map((report) => {
          const maxSeverity = Math.max(...report.flags.map(f => f.severity), 0)
          const date = new Date(report.ts * 1000).toLocaleDateString()
          
          return (
            <div
              key={report.id}
              onClick={() => handleReportClick(report)}
              className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-groq-blue dark:hover:border-groq-blue cursor-pointer transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="font-medium text-gray-900 dark:text-white truncate">
                    {report.doc_name}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  {getSeverityIcon(maxSeverity)}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                {report.summary}
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>{date}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>Risk:</span>
                  <span className={`font-medium ${getRiskColor(report.overall_risk)}`}>
                    {report.overall_risk.toFixed(1)}%
                  </span>
                  <span>({report.flags.length} issues)</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}