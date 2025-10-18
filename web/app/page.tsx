'use client'

import { useState } from 'react'
import { FileUpload } from './components/FileUpload'
import { ComplianceReport } from './components/ComplianceReport'
import { RecentReports } from './components/RecentReports'
import { ThemeToggle } from './components/ThemeToggle'
import { AnalysisResult } from './utils/export'
import { Zap, Shield, Brain, Database } from 'lucide-react'

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [currentDocName, setCurrentDocName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [useStreaming, setUseStreaming] = useState(true)

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result)
    setError(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setAnalysisResult(null)
  }

  const handleCloseReport = () => {
    setAnalysisResult(null)
  }

  const handleReportSelect = (result: AnalysisResult, docName: string) => {
    setAnalysisResult(result)
    setCurrentDocName(docName)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-groq-blue rounded-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  AI Compliance Copilot
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Powered by Groq
                </p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Analyze Financial & Legal Documents
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            Upload PDFs to get instant compliance analysis with AI-powered risk assessment, 
            flag detection, and actionable recommendations.
          </p>
          
          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <Zap className="h-8 w-8 text-groq-blue mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Ultra-Fast Analysis
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Powered by Groq's lightning-fast Llama 3 model
              </p>
            </div>
            
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <Brain className="h-8 w-8 text-groq-blue mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                AI-Powered Detection
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Identifies AML, sanctions, GDPR, and cross-border risks
              </p>
            </div>
            
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <Database className="h-8 w-8 text-groq-blue mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Report History
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Store and access all your compliance reports
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Upload Document
                </h3>
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-600 dark:text-gray-400">
                    Live Streaming
                  </label>
                  <button
                    onClick={() => setUseStreaming(!useStreaming)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      useStreaming ? 'bg-groq-blue' : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        useStreaming ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
              
              <FileUpload
                onAnalysisComplete={handleAnalysisComplete}
                onError={handleError}
                useStreaming={useStreaming}
              />
              
              {error && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Reports */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <RecentReports onReportSelect={handleReportSelect} />
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center">
          <div className="flex items-center justify-center space-x-2 text-gray-500 dark:text-gray-400">
            <span>Powered by</span>
            <a
              href="https://groq.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-groq-blue hover:text-blue-600 font-medium transition-colors"
            >
              Groq
            </a>
            <span>•</span>
            <a
              href="https://supabase.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 hover:text-green-700 font-medium transition-colors"
            >
              Supabase
            </a>
            <span>•</span>
            <a
              href="https://smithery.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-700 font-medium transition-colors"
            >
              Smithery MCP
            </a>
            <span>•</span>
            <a
              href="https://cursor.sh"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              Cursor
            </a>
          </div>
          <div className="mt-2 text-sm text-gray-400">
            Built for Cursor Hackathon Singapore 2025
          </div>
        </footer>
      </main>

      {/* Report Modal */}
      {analysisResult && (
        <ComplianceReport
          result={analysisResult}
          docName={currentDocName}
          onClose={handleCloseReport}
        />
      )}
    </div>
  )
}