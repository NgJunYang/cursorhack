'use client'

import { useState } from 'react'
import { Download, AlertTriangle, CheckCircle, Info, X } from 'lucide-react'
import { AnalysisResult, generateMarkdownReport, downloadMarkdown } from '../utils/export'

interface ComplianceReportProps {
  result: AnalysisResult
  docName: string
  onClose: () => void
}

export function ComplianceReport({ result, docName, onClose }: ComplianceReportProps) {
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const markdown = generateMarkdownReport(result, docName)
      const filename = `compliance-report-${docName.replace('.pdf', '')}-${new Date().toISOString().split('T')[0]}.md`
      downloadMarkdown(markdown, filename)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  const getSeverityColor = (severity: number) => {
    if (severity >= 4) return 'text-red-600 dark:text-red-400'
    if (severity >= 3) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-green-600 dark:text-green-400'
  }

  const getSeverityBg = (severity: number) => {
    if (severity >= 4) return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
    if (severity >= 3) return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
    return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
  }

  const getRiskLevel = (risk: number) => {
    if (risk >= 80) return { label: 'CRITICAL', color: 'text-red-600 dark:text-red-400' }
    if (risk >= 60) return { label: 'HIGH', color: 'text-orange-600 dark:text-orange-400' }
    if (risk >= 40) return { label: 'MEDIUM', color: 'text-yellow-600 dark:text-yellow-400' }
    if (risk >= 20) return { label: 'LOW', color: 'text-green-600 dark:text-green-400' }
    return { label: 'MINIMAL', color: 'text-green-600 dark:text-green-400' }
  }

  const riskLevel = getRiskLevel(result.overall_risk)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Compliance Analysis Report
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Summary Card */}
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
              Executive Summary
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">{result.summary}</p>
            
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-500 dark:text-gray-400">Overall Risk Score:</span>
                <span className={`ml-2 text-2xl font-bold ${riskLevel.color}`}>
                  {result.overall_risk.toFixed(1)}%
                </span>
                <span className={`ml-2 text-sm font-medium ${riskLevel.color}`}>
                  ({riskLevel.label})
                </span>
              </div>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="flex items-center space-x-2 px-4 py-2 bg-groq-blue text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>{isExporting ? 'Exporting...' : 'Download Markdown'}</span>
              </button>
            </div>
          </div>

          {/* Compliance Flags */}
          {result.flags.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Compliance Issues Found ({result.flags.length})
              </h3>
              
              {result.flags.map((flag, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${getSeverityBg(flag.severity)}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                      {flag.title}
                    </h4>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getSeverityColor(flag.severity)}`}>
                        Severity {flag.severity}/5
                      </span>
                      {flag.severity >= 4 ? (
                        <AlertTriangle className="h-5 w-5 text-red-500" />
                      ) : flag.severity >= 3 ? (
                        <Info className="h-5 w-5 text-yellow-500" />
                      ) : (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Why it matters:
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {flag.why_it_matters}
                      </p>
                    </div>

                    <div>
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Recommendation:
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {flag.recommendation}
                      </p>
                    </div>

                    {flag.evidence.length > 0 && (
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Evidence:
                        </h5>
                        <div className="space-y-2">
                          {flag.evidence.map((evidence, evIndex) => (
                            <div
                              key={evIndex}
                              className="p-3 bg-white dark:bg-gray-700 rounded border-l-4 border-groq-blue"
                            >
                              <div className="flex items-start space-x-2">
                                <span className="text-xs font-medium text-groq-blue bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded">
                                  Page {evidence.page}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 italic">
                                "{evidence.quote}"
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No Compliance Issues Found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                This document appears to be compliant with standard regulations.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}