'use client';

import { downloadMarkdown } from '../utils/export';

interface Evidence {
  page: number;
  quote: string;
}

interface Flag {
  title: string;
  severity: number;
  why_it_matters: string;
  recommendation: string;
  evidence: Evidence[];
}

interface Report {
  doc_name: string;
  page_count?: number;
  summary: string;
  overall_risk: number;
  flags: Flag[];
}

interface ReportViewProps {
  report: Report;
}

export default function ReportView({ report }: ReportViewProps) {
  const getSeverityColor = (severity: number) => {
    if (severity <= 2) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (severity === 3) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
  };

  const getRiskColor = (risk: number) => {
    if (risk <= 0.4) return 'text-green-600 dark:text-green-400';
    if (risk <= 0.7) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 space-y-6">
      {/* Summary Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold dark:text-white mb-2">Compliance Report</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Document: {report.doc_name}
              {report.page_count && ` (${report.page_count} pages)`}
            </p>
          </div>
          <button
            onClick={() => downloadMarkdown(report)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Markdown
          </button>
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg font-semibold dark:text-white">Overall Risk:</span>
            <span className={`text-2xl font-bold ${getRiskColor(report.overall_risk)}`}>
              {(report.overall_risk * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                report.overall_risk <= 0.4 ? 'bg-green-500' :
                report.overall_risk <= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${report.overall_risk * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <h3 className="font-semibold mb-2 dark:text-white">Executive Summary</h3>
          <p className="text-gray-700 dark:text-gray-300">{report.summary}</p>
        </div>
      </div>

      {/* Flags Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 dark:text-white">Red Flag Findings</h3>
        <div className="space-y-4">
          {report.flags.map((flag, idx) => (
            <div key={idx} className="border dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <h4 className="text-lg font-semibold dark:text-white">{flag.title}</h4>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(flag.severity)}`}>
                  Severity {flag.severity}/5
                </span>
              </div>
              
              <div className="space-y-2 mb-3">
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Why It Matters: </span>
                  <span className="text-gray-600 dark:text-gray-400">{flag.why_it_matters}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 dark:text-gray-300">Recommendation: </span>
                  <span className="text-gray-600 dark:text-gray-400">{flag.recommendation}</span>
                </div>
              </div>

              {flag.evidence && flag.evidence.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                  <p className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Evidence:</p>
                  <ul className="space-y-1">
                    {flag.evidence.map((ev, evIdx) => (
                      <li key={evIdx} className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-medium">Page {ev.page}:</span> "{ev.quote}"
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
